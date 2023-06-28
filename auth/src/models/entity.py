import uuid
from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy import Boolean, Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from werkzeug.security import check_password_hash


metadata_obj = MetaData(schema="auth")

class Base(DeclarativeBase):
    metadata = metadata_obj


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(50))
    profile = relationship('UserProfile', uselist=False, back_populates='user')
    login_history = relationship('LoginHistory', back_populates='user')

    def __init__(
            self, login: str, hashed_password: str, first_name: str | None,
            last_name: str | None, email = str | None
        ) -> None:
        self.login = login
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'role'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship('UserProfile', back_populates='role')

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'
    

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship('User', back_populates='profile')
    registration_dt = Column(DateTime, default=datetime.now)
    active = Column(Boolean, nullable=False, default=True)
    is_staff = Column(Boolean, default=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('role.id'))
    role = relationship('Role', back_populates='users')

    def __init__(self, user: User, role=None) -> None:
        self.user = user
        self.role = role

    def __repr__(self) -> str:
        return f'<{self.user}\'s profile'


class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship('User', back_populates='login_history')
    user_agent = Column(String(255))
    login_dt = Column(DateTime)

    def __init__(self, user: User, login_dt: datetime) -> None:
        self.login_dt = login_dt
        self.user = user

    def __repr__(self) -> str:
        return f'<{self.user}\'s login history>'
