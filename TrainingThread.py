import asyncio
import threading
import time

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Util import Strings
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
from gdo.core.GDO_User import GDO_User
from gdo.ui.GDT_Page import GDT_Page


class TrainingThread(threading.Thread):
    _genome: GDO_ChatGenome

    INSTANCES = {}

    @classmethod
    def instance(cls, genome: GDO_ChatGenome):
        if genome not in cls.INSTANCES:
            cls.INSTANCES[genome] = cls(genome)
            cls.INSTANCES[genome].start()
        return cls.INSTANCES[genome]

    def __init__(self, genome: GDO_ChatGenome):
        super().__init__()
        self.daemon = True
        self._genome = genome

    def run(self):
        Logger.debug("TrainingThread.run()")
        Application.init_thread(self)
        while Application.RUNNING:
            self.running()
        # del self.INSTANCES[self._genome]

    def running(self):
        if self.has_work_todo():
            try:
                self.chatgpt_request()
            except Exception as ex:
                Logger.exception(ex)
        elif self.can_evolve():
            try:
                self.evolve()
            except Exception as ex:
                Logger.exception(ex)
        else:
            time.sleep(1)

    def has_work_todo(self) -> bool:
        return GDO_ChatMessage.has_work_todo(self._genome)

    def can_evolve(self) -> bool:
        return GDO_ChatMessage.can_evolve(self._genome)

    def chatgpt_request(self):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        server = self._genome.get_server()
        prompt = GDO_ChatMessage.next_prompt(self._genome)
        msgs = prompt.prompt_messages()  # GDO Messages
        messages = GDO_ChatMessage.get_messages(self._genome, msgs)  # json messages
        message = (Message(None, server.get_connector().get_render_mode()).
                   env_user(prompt.get_user()).env_channel(self._genome.get_channel()).env_server(server))
        mod = module_chatgpt.instance()
        api = mod.get_openai()
        response = api.chat.completions.create(
            model=self._genome.get_model_name(),
            messages=messages,
            temperature=self.get_temperature(message),
            # max_tokens=max_tokens,
            # n=n,
            # stop=stop,
            # presence_penalty=presence_penalty,
            # frequency_penalty=frequency_penalty,
        )
        # generated_texts = [
        #     choice.message["content"].strip() for choice in response["choices"]
        # ]
        GDO_ChatMessage.change_state(prompt, msgs, 'answered')
        result = response.choices[0].message.content
        message._result = f"{result} #{prompt.get_id()}"
        message._sender = mod.cfg_chappy()
        asyncio.run(message.deliver())

        if result.startswith('$ack'):
            return prompt.chappy_acknowledged(message)

        message._result = result
        if message._env_user.get_server().get_trigger() in result:
            self.execute_chappy_response(message, prompt)

    def get_temperature(self, message: Message):
        if message._env_channel:
            return self.get_temp_channel(message)
        else:
            return self.get_temp_user(message)

    def get_temp_channel(self, message: Message):
        from gdo.chatgpt.method.ChappyEventListener import ChappyEventListener
        return ChappyEventListener().env_copy(message).cfg_channel_temperature()

    def get_temp_user(self, message: Message):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        return module_chatgpt.instance().cfg_temperature(message._env_user)

    def execute_chappy_response(self, message: Message, prompt: GDO_ChatMessage):
        from gdo.core.GDO_Session import GDO_Session
        Application.fresh_page()
        message._message = message._result
        message.env_user(self.get_chappy())
        message._sender = GDO_User.system()
        message._env_session = GDO_Session.for_user(self.get_chappy())
        message._env_reply_to = 'Chappy'
        parser = self.get_chappy_parser(message)
        command = Strings.substr_from(message._message, message._sender.get_server().get_trigger())
        method = parser.parse(command)
        gdt = method.execute()
        txt = GDT_Page.instance()._top_bar.render_txt()
        txt += " "
        txt += gdt.render_txt()
        message._result = txt.strip()
        message.env_user(prompt.get_user())
        asyncio.run(message.deliver())

    def get_chappy_parser(self, message: Message):
        from gdo.base.Parser import Parser
        from gdo.base.Render import Mode
        from gdo.core.GDO_Session import GDO_Session
        user = message._env_user
        server = user.get_server()
        channel = message._env_channel
        session = GDO_Session.for_user(self.get_chappy())
        return Parser(Mode.TXT, user, server, channel, session)

    def get_chappy(self) -> GDO_User:
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        return module_chatgpt.instance().cfg_chappy()

    def evolve(self):
        GDO_ChatGenomeHistory.init_evolve(self._genome)
        path = Application.file_path(f'files/chatgpt/{self._genome.get_id()}.json')
        messages = GDO_ChatMessage.get_messages(self._genome, False, True)
        messages = {
            "messages": messages,
        }
        Files.put_contents(path, json.dumps(messages))
        client = module_chatgpt.instance().get_openai()
        response = client.files.create(
            file=open(path, "rb"),
            purpose="fine-tune"
        )
        fileid = response.id
        response = client.fine_tuning.jobs.create(
            training_file=fileid,
            model=self._genome.get_model_name(),
        )
        jobid = response.id
        time.sleep(2)
        while True:
            job_status = client.fine_tuning.jobs.retrieve(jobid)
            if job_status.status == 'succeeded':
                model_name = job_status.fine_tuned_model
                GDO_ChatGenomeHistory.evolve(self._genome, model_name)
                GDO_ChatMessage.mark_processed(self._genome)
                break
            elif job_status.status == 'failed':
                Logger.error("Fine-tuning job failed.")
                break
            else:
                time.sleep(10)
