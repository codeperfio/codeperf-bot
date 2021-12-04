import logging

from starlette.config import Config

config = Config(".env")

DB_DRIVER = config("DB_DRIVER", default="redis")
DB_HOST = config("DB_HOST", default="localhost")
CORS_ORIGINS = config("CORS_ORIGINS", default="http://localhost,http://localhost:8080")
DB_PORT = config("DB_PORT", cast=int, default=6379)
DB_USER = config("DB_USER", default=None)
DB_PASSWORD = config("DB_PASSWORD", default=None)
DB_EXPIRE_SECS = config("DB_EXPIRE_SECS", cast=int, default=24 * 30 * 60 * 60)
GH_APP_ID = config("GH_APP_ID", default=None)
GH_SECRET = config("GH_SECRET", default=None)
PORT = config("PORT", default=None)
GH_PRIVATE_KEY = config("GH_PRIVATE_KEY", default=None)


def check_env_var(env_var, env_varname):
    res = False
    if env_var is not None:
        res = True
    else:
        logging.error("Required env var {} is not set".format(env_varname))
    return res
