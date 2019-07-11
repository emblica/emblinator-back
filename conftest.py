import pytest

from app import create_app
from models import db


@pytest.fixture
def test_app():
    return create_app('testing')


@pytest.fixture
def client(test_ctx, test_app):
    return test_app.test_client()


@pytest.fixture
def test_ctx(test_app):
    with test_app.test_request_context() as ctx:
        yield ctx


@pytest.fixture
def database(test_ctx):
    db.drop_all()
    db.create_all()
