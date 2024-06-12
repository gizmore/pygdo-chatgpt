from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDT_ChatMsgState import GDT_ChatMsgState
from gdo.chatgpt.method.ChappyEventListener import ChappyEventListener
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_Text import GDT_Text
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.date.Time import Time


class GDO_ChatMessage(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('gcm_id'),
            GDT_Object('gcm_genome').table(GDO_ChatGenome.table()).not_null(),
            GDT_Object('gcm_prompt_message').table(self.table()),
            GDT_User('gcm_user'),  # 1=system, 2=Chappy (in a normal setup)
            GDT_Text('gcm_text').not_null(),
            GDT_Bool('gcm_prompt').not_null().initial('0'),
            GDT_Bool('gcm_response').not_null().initial('0'),
            GDT_ChatMsgState('gcm_state').initial('created').not_null(),
            GDT_Created('gcm_created'),
        ]

    def get_user(self) -> GDO_User:
        return self.gdo_value('gcm_user')

    def get_genome(self) -> GDO_ChatGenome:
        return self.gdo_value('gcm_genome')

    def get_created(self):
        return self.gdo_val('gcm_created')

    def get_message_text(self) -> str:
        return self.gdo_val('gcm_text')

    def is_prompt(self) -> bool:
        return self.gdo_value('gcm_prompt')

    def is_chappy_response(self) -> bool:
        return self.gdo_value('gcm_response')

    @classmethod
    def get_chappy(cls):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        return module_chatgpt.instance().cfg_chappy()

    @classmethod
    def get_trigger(cls, genome: GDO_ChatGenome):
        channel = genome.get_channel()
        el = ChappyEventListener().env_channel(channel).env_user(genome.get_user()).env_server(genome.get_user().get_server())
        if channel:
            return el.get_config_channel_val('chappy_trigger')
        else:
            return el.get_config_server_val('chappy_trigger')

    @classmethod
    def next_prompt(cls, genome: GDO_ChatGenome):
        return (cls.table().select().where(f"gcm_genome={genome.get_id()} AND gcm_prompt=1 AND gcm_state='created'").
                order('gcm_created ASC').first().exec().fetch_object())

    def prompt_messages(self, max_messages: int = 25):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        lookback = module_chatgpt.instance().cfg_lookback()
        cut = Time.get_date(Application.TIME - lookback)
        genome = self.get_genome()
        query = self.table().select()
        query.where(f"gcm_genome={genome.get_id()}")
        query.where("gcm_state IN ('created', 'answered', 'acknowledged', 'ack')")
        query.where(f"gcm_created>='{cut}' AND gcm_created<='{self.get_created()}'")
        query.order('gcm_created ASC')
        # query.where('gcm_prompt_message IS NULL')
        messages = query.exec().fetch_all()
        return messages[-max_messages:]

    @classmethod
    # def messages_for_prompt(cls, genome: GDO_ChatGenome):
    #     return cls.table().select().where(f"gcm_genome={genome.get_id()} AND gcm_processing IS NULL").order('gcm_created ASC').exec().fetch_all()

    @classmethod
    def get_messages(cls, genome: GDO_ChatGenome, messages: list, with_prompt: bool = True, mark_processing: bool = False):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        back = []
        if with_prompt:
            back.append({"role": "system", "content": genome.get_full_genome()})
        chappy = module_chatgpt.instance().cfg_chappy()
        for message in messages:
            back.append({
                "role": message.get_role(),
                "content": message.get_content(),
            })
            if mark_processing:
                message.save_val('gcm_processing', '0')
                if message.get_user() == chappy:
                    break
        return back

    def get_role(self) -> str:
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        user = self.get_user()
        if user.get_id() == module_chatgpt.instance().cfg_chappy_id():
            return 'assistant'
        return 'user'

    def get_content(self) -> str:
        user = self.get_user()
        return f"[{user.render_name()}]: {self.get_message_text()}"

    @classmethod
    # def mark_processed(cls, genome: GDO_ChatGenome):
    #     return cls.table().update().set('gcm_processing=1').where(f'gcm_genome={genome.get_id()} AND gcm_processing=0').exec()

    @classmethod
    def has_work_todo(cls, genome: GDO_ChatGenome):
        return cls.table().count_where(f"gcm_genome={genome.get_id()} AND gcm_prompt=1 AND gcm_state='created'") > 0

    @classmethod
    def change_state(cls, prompt: 'GDO_ChatMessage', msgs: list['GDO_ChatMessage'], state: str):
        for msg in msgs:
            msg.set_val('gcm_state', state)
            if prompt and not msg.gdo_val('gcm_prompt_message'):
                msg.set_val('gcm_prompt_message', prompt.get_id())
            msg.save()

    def chappy_acknowledged(self, message: Message):
        for msg in self.prompt_messages():
            msg._acknowledge(self, message)
        self.blank({
            'gcm_genome': self.get_genome().get_id(),
            'gcm_prompt_message': self.get_id(),
            'gcm_user': self.get_chappy().get_id(),
            'gcm_text': message._result,
            'gcm_response': '1',
            'gcm_state': 'acknowledged',
        }).insert()

    def _acknowledge(self, prompt: 'GDO_ChatMessage', message: Message):
        if prompt and not self.gdo_val('gcm_prompt_message'):
            self.save_vals({
                'gcm_prompt_message': prompt.get_id(),
                'gcm_state': 'acknowledged',
            })

    ########
    # Nope #
    ########
    def nope_it(self):
        pass

    ##########
    # Evolve #
    ##########
    @classmethod
    def can_evolve(cls, genome: GDO_ChatGenome):
        return cls.table().count_where(f"gcm_genome={genome.get_id()} AND gcm_prompt=1 AND gcm_state='created'") >= 10
