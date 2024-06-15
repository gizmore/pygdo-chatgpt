from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDT_ChatModel import GDT_ChatModel
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_User import GDT_User


class chappy(Method):

    def gdo_trigger(self) -> str:
        return 'chappy'

    def gdo_method_config_channel(self) -> [GDT]:
        return [
            GDT_User('chappy'),
        ]

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_ChatModel('model').initial('agi').not_null(),
            GDT_Enum('state').choices({'on': 'On', 'off': 'Off'}).not_null(),
        ]

    def get_subcommand(self) -> str:
        return self.param_val('state')

    def gdo_execute(self):
        from gdo.chatgpt import module_chatgpt
        hasattr(self, f"{self.get_subcommand()}")
        match self.get_subcommand():
            case 'on':
                if self._env_channel:
                    chappy = module_chatgpt.instance().cfg_chappy(channel=self._env_channel)
                    genome = GDO_ChatGenome.get_or_create_for_channel(self._env_channel, self.parameter('model'))
                else:
                    chappy = module_chatgpt.instance().cfg_chappy(user=self._env_user)
                    genome = GDO_ChatGenome.get_or_create_for_user(self._env_user, self.parameter('model'))
                return self.msg('msg_chappy_enabled', [self.param_val('model')])
            case 'off':
                if self._env_channel:
                    genome = GDO_ChatGenome.get_for_channel(self._env_channel)
                else:
                    genome = GDO_ChatGenome.get_for_user(self._env_user)
                if not genome:
                    return self.err('err_chappy_not_enabled')
                genome.delete()
                return self.msg('msg_chappy_disabled')

        return self

    def render_irc(self) -> str:
        return 'AAA'
