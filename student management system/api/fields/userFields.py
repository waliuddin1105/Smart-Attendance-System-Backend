from marshmallow import Schema, validates, ValidationError, fields
from marshmallow.validate import Length
from api import user_ns
import re   #regex for  password validations
from flask_restx import fields as f

user_data = user_ns.model(
    'Add user data',
    {
        "username" : f.String(required = True, description = 'enter a unique username of atleast 3 characters'),
        "password" : f.String(required = True, description = 'Enter a strong password')
    }
)

class UserSchema(Schema):
    username = fields.Str(required = True, validate = Length(min = 3, error="Username must be atleast 3 characters"))
    password = fields.Str(required= True)

    @validates('password')
    def validate_password(self, value, **kwargs):
        if len(value) < 6:
            raise ValidationError('Password length must be atleast 6 characters')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain atleast one capital letter')
        if not re.search(r"\d", value):
            raise ValidationError('Password must include atleast 1 number')
