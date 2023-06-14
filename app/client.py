"""
Client for websocket-based publisher-subscriber implementation
"""

import asyncio
import threading
import json
import argparse
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError


# custom exception
class KillSignal(Exception):
    pass


def print_commands():
    print("""
-----------------------------------------------------
=========== EchoChat Static CLI Commands ============
-----------------------------------------------------

usage: (python) client.py [options] <command> [args]

>> Commands <<

list
    lists all available topics and returns

status <topic>
    outputs information about the given topic

subscribe <topic>
    subscribes and outputs information when published,
    blocks the terminal

publish <topic> <message>
    subscribes to the topic and publishes the given
    message, blocks the terminal


>> Options <<

--cli, -c
    suppresses interactive interface

--output [type], -o
    selects the output type, either (j)son or (h)uman,
    defaults to json

--help, -h
    prints this list and returns


>> Examples <<

python client.py --cli list

python client.py --cli subscribe General

python client.py --cli publish General "Hello, World!"

    """)

def get_help():
    return """
----------------------------------------------------
======== EchoChat Interactive CLI Commands =========
----------------------------------------------------
-> (s)ubscribe --- subscribe to a topic, creates
                   one if topic does not exist
-> (u)nsubscribe - unsubscribe from a topic
-> (p)ublish ----- send a message to a topic
-> (l)ist -------- list all existing topics
-> s(t)atus ------ check subscription to a topic
-> (h)elp -------- see this menu again
-> (e)xit/(q)uit - stop the client

Hint: run the client with --help to see non-
      interactive command line options
  """

def print_help(_):
    print(get_help())

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

def handle_subscribe(conn, name = ""):
    topic = input("subscribe to topic:\n>> ") if name == "" else name
    send_ws_request("SUBSCRIBE_TOPIC", {"name": topic}, conn)

def handle_unsubscribe(conn, name = ""):
    topic = input("unsubscribe from topic:\n>> ") if name == "" else name
    send_ws_request("UNSUBSCRIBE_TOPIC", {"name": topic}, conn)

def handle_publish(conn, name = "", message = ""):
    topic = input("choose topic to publish to:\n>> ") if name == "" else name
    text = input("message to publish:\n>> ") if message == "" else message
    params = {"name": topic, "message": text}
    send_ws_request("PUBLISH_TOPIC", params, conn)

def handle_list(conn):
    send_ws_request("LIST_TOPICS", {}, conn)

def handle_status(conn, name = ""):
    topic = input("choose topic to check:\n>> ") if name == "" else name
    send_ws_request("GET_TOPIC_STATUS", {"name": topic}, conn)

def end_loop(_):
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
        #print("\nwebsocket closed")
        pass
    except ConnectionClosedError:
        #print("\nwebsocket died")
        pass
    except KillSignal:
        pass
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

def do_args():
    parser = argparse.ArgumentParser(
            prog="client.py",
            description="EchoChat CLI Client",
            )
    parser.add_argument("-c", "--cli", 
                        action="store_true",
                        default=False,
                        help="suppresses interactive interface")
    parser.add_argument("-o", "--output",
                        nargs="?",
                        choices=["json", "human"],
                        default="json",
                        help="selects the output type, either 'json' or 'human', defaults to %(default)s")
    parser.add_argument("command",
                        choices=["list", "status", "subscribe", "publish"],
                        help="the command to be run, either: list, status, subscribe, publish")
    parser.add_argument("-t", "--topic",
                        help="the topic parameter")
    parser.add_argument("-m", "--message",
                        help="the message to publish")
    return parser.parse_args()

def main():
    """
    primary control loop
    """

    # parse command line options    
    args = do_args()
    print(args)

    # connect our client to the server
    uri = "ws://127.0.0.1:8000/ws"
    conn = connect(uri)

    if args.cli:

        # do command line actions
        if args.command == "list":
            handle_list(conn)
            pass
        elif args.command == "status":
            handle_status(conn, args.topic)
            pass
        elif args.command == "subscribe":
            handle_subscribe(conn, args.topic)
            pass
        elif args.command == "publish":
            handle_subscribe(conn, args.topic)
            handle_publish(conn, args.topic, args.message)
            pass

        if args.command in ("subscribe", "publish"):
            try:
                while True:
                    result = conn.recv()
                    print(result)
            except KeyboardInterrupt:
                conn.close()
                pass
        else:
            # wait for server response 
            result = conn.recv()
            print(result)

            # exit
            conn.close()
            exit(0)

    else: 

        # start a new listener thread to receive messages
        listener_loop = start_socket(conn)

        try:
            print_help("")

            while True:
                command = input("> ").lower()
                handle_input(command, conn)

        except KeyboardInterrupt:
            listener_loop.stop()
            conn.close()


if __name__ == "__main__":
    main()
