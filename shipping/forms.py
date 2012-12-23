import wtforms
from wtforms.validators import Optional, Required


class AddPackageForm(wtforms.Form):
    name = wtforms.StringField(validators=[Required()])
    tracking_number = wtforms.StringField(validators=[Required()])
    site = wtforms.StringField()
    description = wtforms.TextAreaField()
