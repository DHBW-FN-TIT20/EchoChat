"""
Client for websocket-based publisher-subscriber implementation
"""

import asyncio
import threading
import json
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

def print_help(conn):
    print("""
------------------------------------------------
======== subscriber interface commands =========
------------------------------------------------
-> (s)ubscribe --- subscribe to a topic, creates
                   one if topic does not exist
-> (u)nsubscribe - unsubscribe from a topic
-> (p)ublish ----- send a message to a topic
-> (l)ist -------- list all existing topics
-> s(t)atus ------ check subscription to a topic
-> (h)elp -------- see this menu again
-> (e)xit/(q)uit - stop the client
          """)

def send_ws_request(function, parameters, conn):
    request = {
        "function": "",
        "parameters": {
        }
    }
    request['function'] = function
    request['parameters'] = parameters
    payload = json.dumps(request)
    conn.send(payload)

def handle_subscribe(conn):
    name = input("subscribe to topic:\n>> ")
    send_ws_request("SUBSCRIBE_TOPIC", {"name": name}, conn)

def handle_unsubscribe(conn):
    name = input("unsubscribe from topic:\n>> ")
    send_ws_request("UNSUBSCRIBE_TOPIC", {"name": name}, conn)

def handle_publish(conn):
    name = input("choose topic to publish to:\n>> ")
    message = input("message to publish:\n>>> ")
    params = {"name": name, "message": message}
    send_ws_request("PUBLISH_TOPIC", params, conn)

def handle_list(conn):
    send_ws_request("LIST_TOPICS", {}, conn)

def handle_status(conn):
    name = input("choose topic to check:\n>> ")
    send_ws_request("GET_TOPIC_STATUS", {"name": name}, conn)

def end_loop(conn):
    print("exiting")
    raise KeyboardInterrupt

def handle_input(input, conn):
    functions = {
            "s": handle_subscribe,
            "subscribe": handle_subscribe,
            "u": handle_unsubscribe,
            "unsubscribe": handle_unsubscribe,
            "p": handle_publish,
            "publish": handle_publish,
            "l": handle_list,
            "list": handle_list,
            "t": handle_status,
            "status": handle_status,
            "h": print_help,
            "help": print_help,
            "e": end_loop,
            "exit": end_loop,
            "quit": end_loop,
            "q": end_loop,
    }
    
    try:
        functions[input.strip()](conn)
    except KeyError:
        # function not available
        print("invalid function")

# adapted from https://stackoverflow.com/a/49899135
async def listener(conn):
    try:
        while True:
            result = conn.recv()
            print(f"\n{result}\n> ", end="")
    except ConnectionClosedOK:
        print("\nwebsocket closed")
    except ConnectionClosedError:
        print("\nwebsocket died")
    except KeyboardInterrupt:
        pass

def start_thread(loop, conn):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listener(conn))

def start_socket(conn):
    worker_loop = asyncio.new_event_loop()
    worker = threading.Thread(target=start_thread, args=(worker_loop, conn))
    worker.start()
    return worker_loop

def main():
    """
    primary control loop
    """

    print_help("")

    uri = "ws://127.0.0.1:8000/ws"
    conn = connect(uri)

    listener_loop = start_socket(conn)

    try:
        while True:
            command = input("> ").lower()
            handle_input(command, conn)

    except KeyboardInterrupt:
        listener_loop.stop()
        conn.close()


if __name__ == "__main__":
    main()
