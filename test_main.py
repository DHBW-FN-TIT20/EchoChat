import unittest

import threading
import asyncio
import subprocess
from time import sleep

import json
from datetime import datetime
import client

from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# adapted from https://stackoverflow.com/a/49899135
async def server_start():
    try:
        subprocess.run(['./venv/bin/uvicorn','main:app', '--host', '127.0.0.1', '--port', '12000'])
    except KeyboardInterrupt:
        pass

def start_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server_start())

def create_server():
    worker_loop = asyncio.new_event_loop()
    worker = threading.Thread(target=start_thread, args=(worker_loop, ))
    worker.start()
    return worker_loop

class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create server instance
        cls.server_thread = create_server()
        sleep(3) # wait a bit for the server to start

        # create client connection
        uri = "ws://127.0.0.1:12000/ws"
        try:
            cls.int = connect(uri)
        except ConnectionClosedOK:
            print("websocket closed")
        except ConnectionClosedError:
            print("websocket closed unexpectedly")

        cls.topic = "test topic"
        cls.subscribed = True

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_thread.stop()
        return super().tearDownClass()

    def test_subscribe(self):
        client.handle_subscribe(self.int, self.topic)

        targetResponse = {
            "status": "success",
            "function": "SUBSCRIBE_TOPIC",
            "data": {
                "topic": self.topic
                },
            "error": ""
        }
        resp = self.int.recv()
        self.assertEqual(resp, json.dumps(targetResponse))
        self.subcribed = True

    def test_list(self):
        client.handle_list(self.int)

        targetResponse = {
            "status": "success",
            "function": "LIST_TOPICS",
            "data": {
                "topic_list": [ self.topic ]
                },
            "error": ""
        }

        resp = self.int.recv()
        self.assertEqual(resp, json.dumps(targetResponse))
        self.subscribed = False

    def test_status(self):
        client.handle_status(self.int, self.topic)

        timestamp = datetime.now().strftime("%Y-%m-%d %X")

        targetResponse = {
            "status": "success",
            "function": "LIST_TOPICS",
            "data": {
                "topic": self.topic,
                "topic_status": "subscribed",
                "last_update": timestamp,
                "subscribers": 1
            },
            "error": ""
        }

        resp = self.int.recv()
        self.assertEqual(resp, json.dumps(targetResponse))
        self.subscribed = False
        pass

    def test_unsubscribe(self):
        client.handle_unsubscribe(self.int, self.topic)

        targetResponse = {
            "status": "success",
            "function": "UNSUBSCRIBE_TOPIC",
            "data": {
                "topic": self.topic
                },
            "error": ""
        }

        resp = self.int.recv()
        self.assertEqual(resp, json.dumps(targetResponse))
        self.subscribed = False

    def test_publish(self):
        pass


if __name__ == '__main__':
    unittest.main()

