from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
from gdo.core.GDT_Object import GDT_Object


class ack(Method):

    def gdo_trigger(self) -> str:
        return 'ack'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Object('id').table(GDO_ChatMessage.table()).not_null(),
        ]

    def gdo_execute(self):
        return self
