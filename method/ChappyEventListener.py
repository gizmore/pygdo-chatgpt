from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDT_ChatTemperature import GDT_ChatTemperature
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_String import GDT_String


class ChappyEventListener(Method):

    def gdo_trigger(self) -> str:
        return ''

    # def gdo_method_config_server(self) -> [GDT]:
    #     return [
    #         GDT_String('chappy_trigger').initial('Chappy'),
    #     ]

    def gdo_method_config_channel(self) -> [GDT]:
        return [
            # GDT_String('chappy_trigger').initial('Chappy'),
            GDT_ChatTemperature('chappy_temperature'),
        ]

    def cfg_channel_temperature(self) -> float:
        return self.get_config_channel_value('chappy_temperature')

    def on_new_message(self, genome: GDO_ChatGenome, message: Message):
        from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
        trigger = genome.get_chappy().get_displayname()
        triggered = message._message.startswith(f"{trigger}:")

        GDO_ChatMessage.blank({
            'gcm_genome': genome.get_id(),
            'gcm_user': message._sender.get_id() if message._sender else message._env_user.get_id(),
            'gcm_text': self.get_db_text2(message),
            'gcm_prompt': '1' if triggered else '0',
        }).insert()

        if triggered:
            from gdo.chatgpt.TrainingThread import TrainingThread
            if Application.is_unit_test():
                TrainingThread(genome).running()
            else:
                TrainingThread.instance(genome)

    def on_message_sent(self, genome: GDO_ChatGenome, message: Message, chappy: GDO_User):
        from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
        prompt = GDO_ChatMessage.current_prompt(genome)
        GDO_ChatMessage.blank({
            'gcm_genome': genome.get_id(),
            'gcm_user': message._sender.get_id() if message._sender else message._env_user.get_id(),
            'gcm_text': self.get_db_text(message),
            'gcm_response': '1' if message._sender == chappy else '0',
            'gcm_state': 'answered' if message._sender == chappy else 'created',
            'gcm_prompt_message': prompt.get_id() if prompt else None,
        }).insert()

    def get_db_text(self, message: Message) -> str:
        if self.is_chappy(message):
            return Strings.rsubstr_to(res, ' #', res)
        return res

    def is_chappy(self, message: Message):
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        chappy = module_chatgpt.instance().cfg_chappy_for_message(message)
        return message._env_reply_to.lower() == 'chappy' or message._sender == chappy

    def get_db_text2(self, message: Message) -> str:
        if self.is_chappy(message):
            return Strings.rsubstr_to(message._message, ' #', message._message)
        return message._message
