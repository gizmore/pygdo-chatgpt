from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDT_ChatModel import GDT_ChatModel
from gdo.core.GDT_Enum import GDT_Enum


class chappy(Method):

    def gdo_trigger(self) -> str:
        return 'chappy'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_ChatModel('model').initial('agi').not_null(),
            GDT_Enum('state').choices({'on': 'On', 'off': 'Off'}).not_null(),
        ]

    def get_subcommand(self) -> str:
        return self.param_val('state')

    def gdo_execute(self):
        hasattr(self, f"{self.get_subcommand()}")
        match self.get_subcommand():
            case 'on':
                if self._env_channel:
                    genome = GDO_ChatGenome.get_or_create_for_channel(self._env_channel, self.parameter('model'))
                else:
                    genome = GDO_ChatGenome.get_or_create_for_user(self._env_user, self.parameter('model'))
                return self.msg('msg_chappy_enabled', [self.param_val('model')])
            case 'off':
                genome = GDO_ChatGenome.get_for_channel(self._env_channel)

        return self

    def render_irc(self) -> str:
        return 'AAA'
