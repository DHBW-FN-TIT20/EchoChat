# EchoChat
A publisher-subscriber based chat system

## Dependencies
 - Python >=3.10
 - Uvicorn
 - Websockets
 - FastAPI

## Installation

```
pip3 install fastapi
pip3 install uvicorn
pip3 install websockets

testing:
pip3 install pytest
```

Start the server with: `uvicorn main:app`.
This will start a server available at `http://127.0.0.1:8000` by default
