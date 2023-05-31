import asyncio
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import uuid
import json

from datetime import datetime
import pprint

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
async def getRoot():
    return FileResponse('index.html')

@app.get("/int")
async def getInterface():
    return FileResponse('interface.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()

    id = uuid.uuid4()

    try:
        # Keep the connection open and handle incoming messages
        while True:
            # Wait for incoming message from the client
            input = await websocket.receive_text()
            response = handle_input(input, id, websocket)

            pprint.pprint(topics)

            # Send the received message to all connected clients
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        # Remove the connection from the list when the client disconnects
        pass

""" 
contains the topics and their relevant subscribers
 .---------------.
 | topics (dict) |
 '--.------------'
    |-[topic] -> subscribers (list), last_update (timestamp)
    |            |- [uuid, conn]
    |            '- [uuid, conn]
    |-[topic] -> subscribers, last_update
    |            '- [uuid, conn]
    '-[topic] -> subscribers, last_update
                 |- [uuid, conn]
                 '- [uuid, conn]
"""
topics = {}

def handle_subscribe(parameters, id, conn):
    """
    add user to topic subscribers list
    """
    response = {
        "status": "failure",
        "function": "SUBSCRIBE_TOPIC",
        "data": {
            "topic": parameters['name'],
        },
        "error": ""
    }
    try:
        subscribers = topics[response['data']['topic']]['subscribers']
        in_list = False
        for sub in subscribers:
            if sub['uuid'] == id:
                in_list = True
                break
        if not in_list:
            topics[response['data']['topic']]['subscribers'].append({"uuid": id, "conn": conn})
            response['status'] = "success"
        else:
            response['error'] = "you are already subscribed to that list"
    except KeyError:
        # key does not exist in topics, create topic
        topics[response['data']['topic']] = {"subscribers": [], "last_update": "never"}
        topics[response['data']['topic']]['subscribers'].append({"uuid": id, "conn": conn})
        response['status'] = "success"

    return response

def handle_unsubscribe(parameters, id, conn):
    """
    remove user from topic
    """
    response = {
        "status": "failure",
        "function": "UNSUBSCRIBE_TOPIC",
        "data": {
            "topic": parameters['name'],
        },
        "error": ""
    }
    try:
        subscribers = topics[response['data']['topic']]['subscribers']
        in_list = False
        for sub in subscribers:
            if sub['uuid'] == id:
                in_list = True
                topics[response['data']['topic']]['subscribers'].remove(sub)    

                # remove topic if all users are unsubscribed
                if len(topics[response['data']['topic']]['subscribers']) == 0:
                    topics.pop(response['data']['topic'], None)

                response['status'] = "success"
                break
        if not in_list:
            response['error'] = "you are not subscribed to that topic"
    except KeyError:
        response['error'] = "topic does not exist"
        pass

    return response

def handle_publish(parameters, id, conn):
    """
    send message to topic subscriber
    """
    response = {
        "status": "failure",
        "function": "PUBLISH_TOPIC",
        "data": {
            "topic": parameters['name'],
            "message": parameters['message'],
        },
        "error": ""
    }

    try:
        subscribers = topics[response['data']['topic']]['subscribers']
        in_list = False
        for sub in subscribers:
            if sub['uuid'] == id:
                # user is subscribed to the list
                in_list = True
                break
        if not in_list:
            response['error'] = "you are not subscribed to that topic"
        else:
            response['status'] = "success"
            timestamp = datetime.now().strftime("%Y-%m-%d %X")
            topics[response['data']['topic']]['last_update'] = timestamp
            start_sender(response['data']['message'], response['data']['topic'], timestamp)
    except KeyError:
        # key(topic) does not exist in topics
        response['error'] = "topic does not exist"

    return response

async def send_update(message, topic, time):
    payload = {
        "status": "success",
        "function": "UPDATE_TOPIC",
        "data": {
            "name": topic,
            "message": message,
            "timestamp": time
        },
        "error": ""
    }
    for sub in topics[topic]['subscribers']:
        await sub['conn'].send_text(json.dumps(payload))

def start_thread(loop, message, topic, time):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_update(message, topic, time))

def start_sender(message, topic, time):
    worker_loop = asyncio.new_event_loop()
    worker = threading.Thread(target=start_thread, args=(worker_loop, message, topic, time))
    worker.start()

    # worker_loop.call_soon_threadsafe(send_update, message, topic, time)


def handle_topic_status(parameters, id, conn):
    """
    tells the user if they are subscribed or not
    """
    response = {
        "status": "failure",
        "function": "GET_TOPIC_STATUS",
        "data": {
            "topic": parameters['name'],
            "topic_status": "",
            "last_update": "",
            "subscribers": "",
        },
        "error": ""
    }

    try:
        subscribers = topics[response['data']['topic']]['subscribers']
        in_list = False
        for sub in subscribers:
            if sub['uuid'] == id:
                # user is subscribed to the list
                in_list = True
                break

        response['status'] = "success"

        if in_list:
            response['data']['topic_status'] = "subscribed"
        else:
            response['data']['topic_status'] = "not subscribed"

        response['data']['subscribers'] = len(subscribers)
        response['data']['last_update'] = topics[response['data']['topic']]['last_update']
    except:
        # key(topic) does not exist in topics
        response['error'] = "topic does not exist"

    return response

def handle_topic_list(parameters, id, conn):
    """
    give the user a list of available topics
    """
    response = {
        "status": "failure",
        "function": "LIST_TOPICS",
        "data": {
            "topic_list": [key for key in topics.keys()],
        },
        "error": ""
    }
    response['status'] = "success"

    return response

def handle_input(input, id, conn):
    functions = {
        'SUBSCRIBE_TOPIC': handle_subscribe, 
        'UNSUBSCRIBE_TOPIC': handle_unsubscribe, 
        'PUBLISH_TOPIC': handle_publish, 
        'GET_TOPIC_STATUS': handle_topic_status, 
        'LIST_TOPICS': handle_topic_list,
    }
    try:
        parsed = json.loads(input)
        return functions[parsed['function']](parsed['parameters'], id, conn)
    except (json.JSONDecodeError, KeyError):
        response = {
            "status": "failure",
            "error": "could not interpret request"
        }
        return response

