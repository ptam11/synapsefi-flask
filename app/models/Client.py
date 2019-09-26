from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()


class Client:
    CLIENT_ID = getenv(
        "CLIENT_ID", "client_id_2bb1e412edd311e6bd04e285d6015267")
    CLIENT_SECRET = getenv(
        "CLIENT_SECRET", "client_secret_6zZVr8biuqGkyo9IxMO5jY2QlSp0nmD4EBAgKcJW")
    USER_ID = getenv(
        "USER_ID", "e83cf6ddcf778e37bfe3d48fc78a6502062fc")
    BASE_URL = "https://uat-api.synapsefi.com/v3.1"
    GATEWAY = f'{CLIENT_ID}|{CLIENT_SECRET}'
    USER_IP = "127.0.0.1"
    USER = f'|{USER_ID}'
    CONTENT_TYPE = "application/json"
    HEADERS = {
        "X-SP-GATEWAY": GATEWAY,
        "X-SP-USER-IP": USER_IP,
        "X-SP-USER": USER,
        "Content-Type": CONTENT_TYPE
    }
