import wtforms
from wtforms.validators import Optional, Required

from shipping import api as shapi


class AddPackageForm(wtforms.Form):
    name = wtforms.StringField(validators=[Required()])
    tracking_number = wtforms.StringField(validators=[Required()])
    carrier = wtforms.SelectField(choices=shapi.CARRIER_LIST)
    site = wtforms.StringField()
    description = wtforms.TextAreaField()


class EditPackageForm(AddPackageForm):
    pass
