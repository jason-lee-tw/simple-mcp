from fastapi import FastAPI
from server_config.server import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)
