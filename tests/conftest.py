import pytest
from pydantic import BaseSettings

from beanita.client import Client


class Settings(BaseSettings):
    mongodb_path: str = "beanita_path"
    mongodb_db_name: str = "beanie_db"


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture()
def cli(settings, loop):
    return Client(settings.mongodb_path)


@pytest.fixture()
def db(cli, settings, loop):
    return cli[settings.mongodb_db_name]
