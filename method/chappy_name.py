from gdo.base.GDT import GDT
from gdo.base.Util import html
from gdo.chatgpt.module_chatgpt import module_chatgpt
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_UserName import GDT_UserName
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Validator import GDT_Validator
from gdo.form.MethodForm import MethodForm


class chappy_name(MethodForm):

    def gdo_trigger(self) -> str:
        return 'chapname'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_UserName('name').not_null(),
            GDT_Validator().validator(form, 'name', self.validate_name),
        )

    def validate_name(self, form: GDT_Form, field: GDT_UserName, value: str) -> bool:
        count = GDO_User.table().count_where(f"user_name={GDT.quote(value)} AND user_id!={self._env_user.get_id()}")
        if count:
            return field.error('err_username_taken')
        return True

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UserName('name').not_null(),
        ]

    def gdo_execute(self):
        name = self.param_val('name')
        chappy = module_chatgpt.instance().cfg_chappy(user=self._env_user)
        chappy.save_val('user_displayname', name)
        return self.msg('msg_chappy_name_changed', [html(name)])
