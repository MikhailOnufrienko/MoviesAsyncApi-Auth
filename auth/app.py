from flask import Flask
from flask_restful import Resource, Api
from auth.db.db import db, init_db

from auth.user.routes import create_authentication_routes
from auth.user.views import RegisterApi


app = Flask(__name__)

api = Api(app)

create_authentication_routes(api=api)


def main():
    init_db(app)
    app.run(debug=True)

    return app


if __name__ == '__main__':
    main()
