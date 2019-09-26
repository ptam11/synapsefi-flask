from os import getenv, environ
from flask import Flask
from dotenv import load_dotenv
from app.controllers.user import user
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = getenv(
    "MONGO_URI", "users")
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY', "it's a secret")

    """
    client credentials set up
    """
    app.config["CLIENT_ID"] = getenv(
        "CLIENT_ID", "client_id_2bb1e412edd311e6bd04e285d6015267")
    app.config["CLIENT_SECRET"] = getenv(
        "CLIENT_SECRET", "client_secret_6zZVr8biuqGkyo9IxMO5jY2QlSp0nmD4EBAgKcJW")
    app.config["USER_ID"] = getenv(
    "USER_ID", "e83cf6ddcf778e37bfe3d48fc78a6502062fc")
    
    from app.mongo import mongo
    mongo.init_app(app)
    app.register_blueprint(user, url_prefix='/')

    return app