from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_UserName import GDT_UserName


class chappy_name(Method):

    def gdo_trigger(self) -> str:
        return 'chapname'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UserName('name').not_null(),
        ]

    def gdo_execute(self):
        pass
