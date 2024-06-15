from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.chatgpt.GDT_DalleModel import GDT_DalleModel
from gdo.core.GDT_RestOfText import GDT_RestOfText


class dalle(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_DalleModel('model').not_null().initial('dalle-3'),
            GDT_RestOfText('prompt').not_null(),
        ]

    def gdo_execute(self):
        pass
