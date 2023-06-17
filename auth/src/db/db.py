import os
import redis
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

db = SQLAlchemy()
redis_db = redis.Redis(host='localhost', port=6379, db=0)


dsl = os.getenv('SQLALCHEMY_DATABASE_URI')


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = dsl
    db.init_app(app) 
