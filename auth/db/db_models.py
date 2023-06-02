"""Data models."""

import uuid
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from auth.db.db import db


class User(db.Model):
    """A data model for user accounts."""

    __tablename__: str = 'users'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs: str) -> None:
        """Take in a dictionary of kw-arguments and
        assign the values to the class attributes.

        """
        self.login = kwargs.get("login")
        self.password = kwargs.get("password")

    def __repr__(self) -> str:
        """Represent a user object as a string."""

        return f'<User {self.login}>'
    
    def hash_password(self) -> None:
        """
        Take the password the user entered, hash it and
        then store the hashed password in the DB.

        """
        self.password = generate_password_hash(self.password).decode("utf8")

    def check_password(self, password: str) -> bool:
        """Take a plaintext password, hash it and compare
        to the hashed password stored in the DB.
        
        :param password: The password to be checked.
        :return: The password is being returned.
        """
        return check_password_hash(self.password, password)
