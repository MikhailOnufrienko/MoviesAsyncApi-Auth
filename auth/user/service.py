import json
import jwt
import datetime
from auth.db.db import db
from os import environ
from auth.db.db_models import LoginHistory, User
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from utils.common import generate_response, TokenGenerator
from utils.validation import (
    CreateLoginInputSchema, CreateRegisterInputSchema, ResetPasswordInputSchema,
)
from utils.http_code import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST


def create_user(request, input_data):
    """
    It creates a new user
    :param request: The request object
    :param input_data: This is the data that is passed to the function
    :return: A response object
    """
    create_validation_schema = CreateRegisterInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)
    check_username_exists = User.query.filter_by(
        login=input_data.get("login")
    ).first()
    if check_username_exists:
        return generate_response(
            message="Username already exists", status=HTTP_400_BAD_REQUEST
        )

    new_user = User(**input_data)  # Create an instance of the User class
    new_user.hash_password()
    db.session.add(new_user)  # Adds new User record to database
    db.session.commit()
    del input_data["password"]
    return generate_response(
        data=input_data, message="User Created", status=HTTP_201_CREATED
    )


def login_user(request, input_data):
    """
    It takes in a request and input data, validates the input data, checks if the user exists, checks if
    the password is correct, and returns a response
    :param request: The request object
    :param input_data: The data that is passed to the function
    :return: A dictionary with the keys: data, message, status
    """
    
    print(request)
    create_validation_schema = CreateLoginInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)

    user = User.query.filter_by(login=input_data.get("login")).first()
    
    if user is None:
        return generate_response(message="User not found", status=HTTP_400_BAD_REQUEST)
    
    hash = generate_password_hash(user.password)
    if check_password_hash(hash, user.password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        user_agent = request.headers['user_agent']
        add_record_to_login_history(user, user_agent) # add a record to the login history

        data = dict(access_token=access_token,refresh_token=refresh_token)

        return generate_response(
            data=data, message="User login successfully", status=HTTP_201_CREATED
        )
    else:
        return generate_response(
            message="Password is wrong", status=HTTP_400_BAD_REQUEST
        )


def reset_password(request, input_data, token):
    create_validation_schema = ResetPasswordInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)
    if not token:
        return generate_response(
            message="Token is required!",
            status=HTTP_400_BAD_REQUEST,
        )
    token = TokenGenerator.decode_token(token)
    user = User.query.filter_by(id=token.get('id')).first()
    if user is None:
        return generate_response(
            message="No record found with this login, please signup first.",
            status=HTTP_400_BAD_REQUEST,
        )
    user = User.query.filter_by(id=token['id']).first()
    user.password = generate_password_hash(input_data.get('password')).decode("utf8")
    db.session.commit()
    return generate_response(
        message="New password successfully set.", status=HTTP_200_OK
    )


def add_record_to_login_history(user: User, user_agent: str):
    
    new_session = LoginHistory(user_id=user.id,
                               user_agent=user_agent,
                               auth_date=datetime.now())
    db.session.add(new_session)
    db.session.commit()
