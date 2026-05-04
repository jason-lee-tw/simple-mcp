from fastapi import FastAPI
from fastapi.testclient import TestClient
from modules.root.root_controller import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_get_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200
