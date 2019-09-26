from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, Regexp, NumberRange
import re


def is_valid_phone_num(num_str):
    return len(num_str) == 10


class UserAddForm(FlaskForm):
    """Form for adding users."""
    # synapse phone number format
    phone_number_regex = re.compile(r'\d\d\d\.\d\d\d\.\d\d\d\d')

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Legal Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Regexp(
        phone_number_regex, flags=0, message="should be in 123.123.1234 format")])

class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class AccountAddForm(FlaskForm):
    account_type = SelectField("Account Type", choices=[("ACH-US", "ACH-US"),  ("CHECK-US", "CHECK-US"), ("CLEARING-US", "CLEARING-US"),  ("CRYPTO-US", "CRYPTO-US"), ("CUSTODY-US", "CUSTODY-US"),  ("DEPOSIT-US", "DEPOSIT-US"), ("IB-DEPOSIT-US", "IB-DEPOSIT-US"),  ("IB-SUBACCOUNT-US", "IB-SUBACCOUNT-US"), ("INTERCHANGE-US", "INTERCHANGE-US"),  ("IOU", "IOU"), ("LOAN-US", "LOAN-US"),  ("WIRE-US", "WIRE-US"), ("WIRE-INT", "WIRE-INT")], validators=[DataRequired()])
    account_name = StringField('Account Name', validators=[DataRequired()])

class TransactionAddForm(FlaskForm):
    from_account = SelectField("From Account", coerce=int)
    to_account = SelectField("To Account", coerce=int)
    amount = FloatField('Amount to Transfer', validators=[DataRequired()])
