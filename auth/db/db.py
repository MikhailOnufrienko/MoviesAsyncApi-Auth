import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
redis_db = redis.Redis(host='localhost', port=6379, db=0)


dsl = 'postgresql://<username>:<password>@<host>/<database_name>'


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = dsl
    db.init_app(app) 
