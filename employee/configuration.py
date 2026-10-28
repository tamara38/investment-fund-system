from datetime import timedelta;
import os;

class Configuration():
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"];
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1);
    REDIS_HOST = os.environ["REDIS_HOST"];
    REDIS_PORT = int(os.environ["REDIS_PORT"]);
    REDIS_ORDER_LIST = os.environ["REDIS_ORDER_LIST"];
    MONGO_HOST = os.environ["MONGO_HOST"];
    MONGO_PORT = int(os.environ["MONGO_PORT"]);
    MONGO_USERNAME = os.environ["MONGO_USERNAME"];
    MONGO_PASSWORD = os.environ["MONGO_PASSWORD"];