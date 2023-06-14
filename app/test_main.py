from fastapi.testclient import TestClient
from .main import app

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive()
        assert data == {"msg": "yeet"}

