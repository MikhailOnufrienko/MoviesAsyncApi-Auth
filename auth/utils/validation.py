from marshmallow import Schema, fields, validate


class CreateRegisterInputSchema(Schema):
    """SignUp fields validation.
    Login must be at least 4 characters, password at least 6 characters.

    """
    login = fields.Str(required=True, validate=validate.Length(min=4))
    password = fields.Str(required=True, validate=validate.Length(min=6))


class CreateLoginInputSchema(Schema):

    password = fields.Str(required=True, validate=validate.Length(min=6))


class ResetPasswordInputSchema(Schema):
    
    password = fields.Str(required=True, validate=validate.Length(min=6))
    