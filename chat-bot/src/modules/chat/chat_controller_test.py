from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from modules.chat.chat_controller import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_chat_endpoint_uses_message_from_request_body():
    with patch("modules.chat.chat_controller.ClaudeAgent") as MockAgent:
        mock_instance = MagicMock()
        mock_instance.chat_with_mcp.return_value = "Hello back"
        MockAgent.return_value = mock_instance

        response = client.post("/chat/", json={"message": "hi there"})

        assert response.status_code == 200
        mock_instance.chat_with_mcp.assert_called_once_with("hi there")
