from api import auth_ns
from flask_restx import fields as f
from marshmallow import fields, ValidationError, Schema
from marshmallow.validate import Length

class UserLoginSchema(Schema):
    username = fields.Str(required=True, validate=Length(min = 3, error = "username must have atleast 3 characters"))
    password = fields.Str(required=True)

login_data = auth_ns.model(
    'Login User',
    {
        "username" : f.String(required = True, description = 'Enter username'),
        "password" : f.String(required = True, description = 'Enter password')
    }
)