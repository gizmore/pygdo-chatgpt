from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.chatgpt.GDT_ChatModel import GDT_ChatModel
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Channel import GDT_Channel
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Text import GDT_Text
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Deleted import GDT_Deleted


class GDO_ChatGenome(GDO):

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('cg_id'),
            GDT_User('cg_user'),
            GDT_Channel('cg_channel'),
            GDT_ChatModel('cg_base_model'),
            GDT_String('cg_model_name'),
            GDT_Text('cg_genome'),
            GDT_Deleted('cg_deleted'),
        ]

    def get_user(self) -> GDO_User:
        return self.gdo_value('cg_user')

    def get_channel(self) -> GDO_Channel:
        return self.gdo_value('cg_channel')

    def get_server(self) -> GDO_Server:
        channel = self.get_channel()
        if channel:
            return channel.get_server()
        user = self.get_user()
        return user.get_server()

    def get_base_model(self) -> GDT_ChatModel:
        return self.column('cg_base_model')

    def get_model_name(self) -> str:
        return self.gdo_val('cg_model_name')

    def get_full_genome(self):
        gdt = self.get_base_model()
        base = gdt.chat_system_genome()
        agi = self.gdo_val('cg_genome')
        if agi:
            base += "\n" + agi
        return base

    @classmethod
    def for_message(cls, message: Message):
        if message._env_channel:
            return cls.get_for_channel(message._env_channel)
        else:
            return cls.get_for_user(message._env_user)

    @classmethod
    def get_for_user(cls, user: GDO_User):
        return cls.table().get_by('cg_user', user.get_id())

    @classmethod
    def get_for_channel(cls, channel: GDO_Channel):
        return cls.table().get_by('cg_channel', channel.get_id())

    @classmethod
    def create_for_channel(cls, channel: GDO_Channel, model: GDT_ChatModel):
        return cls.blank({
            'cg_channel': channel.get_id(),
            'cg_base_model': model.get_val(),
            'cg_model_name': model.base_model(),
        }).insert()

    @classmethod
    def create_for_user(cls, user: GDO_User, model: GDT_ChatModel):
        return cls.blank({
            'cg_user': user.get_id(),
            'cg_base_model': model.get_val(),
            'cg_model_name': model.base_model(),
        }).insert()

    @classmethod
    def get_or_create_for_channel(cls, channel: GDO_Channel, model: GDT_ChatModel):
        genome = cls.get_for_channel(channel)
        if not genome:
            genome = cls.create_for_channel(channel, model)
        else:
            genome.save_val('cg_base_model', model.get_val())
        return genome

    @classmethod
    def get_or_create_for_user(cls, user: GDO_User, model: GDT_ChatModel):
        genome = cls.get_for_user(user)
        if not genome:
            genome = cls.create_for_user(user, model)
        else:
            genome.save_val('cg_base_model', model.get_val())
        return genome

    def reset(self):
        from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
        GDO_ChatMessage.reset(self)

    def evolve(self, model_name: str):
        self.save_val('cg_model_name', model_name)
        pass

    def get_chappy(self) -> GDO_User:
        from gdo.chatgpt.module_chatgpt import module_chatgpt
        if channel := self.get_channel():
            return module_chatgpt.instance().cfg_chappy(channel=channel)
        elif user := self.get_user():
            return module_chatgpt.instance().cfg_chappy(user=user)
        else:
            return module_chatgpt.instance().cfg_chappy()
