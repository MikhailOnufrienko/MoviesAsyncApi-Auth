from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Resource, Api
from auth.db.db import db, init_db

from auth.user.routes import create_authentication_routes
from auth.user.views import RegisterApi
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

api = Api(app)

create_authentication_routes(api=api)


def main():
    init_db(app)
    app.run(debug=True)

    return app


if __name__ == '__main__':
    main()
