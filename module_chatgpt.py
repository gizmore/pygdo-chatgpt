import functools

import tomlkit

from openai import OpenAI

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Util import Files, Strings
from gdo.chatgpt.GDO_ChatGenome import GDO_ChatGenome
from gdo.chatgpt.GDO_ChatGenomeHistory import GDO_ChatGenomeHistory
from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
from gdo.chatgpt.GDT_ChatTemperature import GDT_ChatTemperature
from gdo.chatgpt.method.ChappyEventListener import ChappyEventListener
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_User import GDT_User
from gdo.core.connector.Bash import Bash
from gdo.date.GDT_Duration import GDT_Duration


class module_chatgpt(GDO_Module):

    ##########
    # Config #
    ##########
    def gdo_module_config(self) -> list[GDT]:
        apikey = ''
        try:
            path = self.file_path('secrets.toml')
            with open(path, 'r') as file:
                toml = tomlkit.load(file)
                apikey = toml['chatgpt_api_key']
        except FileNotFoundError:
            pass
        return [
            GDT_Secret('chatgpt_api_key').initial(apikey),
            GDT_User('chatgpt_chappy'),
            GDT_Duration('chatgpt_lookback').initial('666'),
        ]

    def cfg_api_key(self) -> str:
        return self.get_config_val('chatgpt_api_key')

    def cfg_chappy(self, user: GDO_User = None, channel: GDO_Channel = None) -> GDO_User:
        """
        Get the chappy user for a user (private chat) or channel.
        Every chappy scope needs a real user, as it is self-aware with own stats.
        Fallback to Chappy{1}
        """
        if user is not None:
            return self.get_or_create_user_chappy(user)
        if channel is not None:
            return self.get_or_create_channel_chappy(channel)
        return self.get_config_value('chatgpt_chappy')

    def cfg_chappy_for_message(self, message):
        if message._env_channel:
            return self.cfg_chappy(channel=message._env_channel)
        elif message._env_user.is_type('device'):
            return self.cfg_chappy(user=message._env_user.get_linked_user())
        else:
            return self.cfg_chappy(user=message._env_user)

    def get_or_create_user_chappy(self, user: GDO_User) -> GDO_User:
        bash_id = Bash.get_server().get_id()
        chappy = GDO_User.table().get_by_vals({
            'user_type': 'device',
            'user_link': user.get_id(),
            'user_server': bash_id,
        })
        if not chappy:
            name = f"UserChappy{user.get_id()}"
            chappy = GDO_User.blank({
                'user_type': 'device',
                'user_name': name,
                'user_displayname': 'Chappy',
                'user_server': bash_id,
                'user_link': user.get_id(),
            }).insert()
        return chappy

    def get_or_create_channel_chappy(self, channel: GDO_Channel) -> GDO_User:
        name = f"Chappy{channel.get_id()}"
        bash_id = Bash.get_server().get_id()
        chappy = GDO_User.table().get_by_vals({
            'user_name': name,
            'user_server': bash_id,
        })
        if not chappy:
            chappy = GDO_User.blank({
                'user_type': 'member',
                'user_name': name,
                'user_displayname': 'Chappy',
                'user_server': bash_id,
            }).insert()
        return chappy

    def cfg_chappy_id(self) -> str:
        return self.get_config_val('chatgpt_chappy')

    def cfg_lookback(self) -> float:
        return self.get_config_value('chatgpt_lookback')

    #################
    # User Settings #
    #################
    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_ChatTemperature('chappy_temperature'),
            GDT_User('chappy_id'),
            GDT_Bool('chappy_no'),
        ]

    def cfg_temperature(self, user: GDO_User):
        return user.get_setting_value('chappy_temperature')

    ###########
    # Install #
    ###########
    def gdo_classes(self):
        return [
            GDO_ChatGenome,
            GDO_ChatGenomeHistory,
            GDO_ChatMessage,
        ]

    def gdo_install(self):
        chappy = Bash.get_server().get_or_create_user('Chappy')
        self.save_config_val('chatgpt_chappy', chappy.get_id())
        Files.create_dir(Application.file_path('files/chatgpt/'))

    def gdo_init(self):
        Application.EVENTS.subscribe('new_message', self.on_new_message)
        Application.EVENTS.subscribe('msg_sent', self.on_message_sent)

    ##########
    # Events #
    ##########

    def on_new_message(self, message: Message):
        if not message._env_user.get_setting_value('chappy_no'):
            genome = GDO_ChatGenome.for_message(message)
            if genome:
                ChappyEventListener().env_copy(message).on_new_message(genome, message)

    def on_message_sent(self, message: Message):
        if not message._env_user.get_setting_value('chappy_no'):
            genome = GDO_ChatGenome.for_message(message)
            if genome:
                if message._result.startswith('Chappy:'):
                    message._message = message._result
                    ChappyEventListener().env_copy(message).on_new_message(genome, message)
                else:
                    chappy = genome.get_chappy()
                    ChappyEventListener().env_copy(message).on_message_sent(genome, message, chappy)

    #######
    # API #
    #######
    @functools.cache
    def get_openai(self) -> OpenAI:
        client = OpenAI(api_key=self.cfg_api_key())
        return client
