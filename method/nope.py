from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.chatgpt.GDO_ChatMessage import GDO_ChatMessage
from gdo.core.GDT_Object import GDT_Object


class nope(Method):

    def gdo_trigger(self) -> str:
        return 'nope'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_Object('prompt').not_null(),
        ]

    def get_prompt(self) -> GDO_ChatMessage:
        return self.param_value('prompt')

    def gdo_execute(self):
        prompt = self.get_prompt()
        if not prompt.is_prompt():
            return self.err('err_chatgpt_prompt_no_prompt')
        prompt.nope_it()
        return self.msg('msg_chatgpt_prompt_nope')
