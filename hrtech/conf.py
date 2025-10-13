from decouple import config
import os
from decouple import Config, RepositoryEnv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOTENV_FILE = BASE_DIR / "env" / ".env"
config = Config(RepositoryEnv(str(DOTENV_FILE)))

ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("ENV_ID", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)