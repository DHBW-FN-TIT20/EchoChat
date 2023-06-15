"""
Client for websocket-based publisher-subscriber implementation
"""

import asyncio
import threading
import json
import argparse
import sys
import textwrap
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError


def get_help():
    """ returns the list of available interactive commands """
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
    """ prints list of available interactive commands """
    print(get_help())

def send_ws_request(function, parameters, conn):
    """
    creates a valid json request and sends it over the given connection
    function(str): a valid echochat server function
    parameters(lst): all required parameters for the request
    conn(websocket): the websocket connection
    """
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
    """
    subscribes the user to the given topic
    conn(websocket): a valid connection to the echochat server
    name(str): the topic to subscribe to
    """
    topic = input("Subscribe to topic:\n>> ") if name == "" else name
    send_ws_request("SUBSCRIBE_TOPIC", {"name": topic}, conn)

def handle_unsubscribe(conn, name = ""):
    """
    unsubscribes the user from the given topic
    conn(websocket): a valid connection to the echochat server
    name(str): the topic to unsubscribe from
    """
    topic = input("Unsubscribe from topic:\n>> ") if name == "" else name
    send_ws_request("UNSUBSCRIBE_TOPIC", {"name": topic}, conn)

def handle_publish(conn, name = "", message = ""):
    """
    publishes the given message to the given topic
    conn(websocket): a valid connection to the echochat server
    name(str): the topic to publish to
    message(str): the message to publish
    """
    topic = input("Choose topic to publish to:\n>> ") if name == "" else name
    text = input("Message to publish:\n>> ") if message == "" else message
    params = {"name": topic, "message": text}
    send_ws_request("PUBLISH_TOPIC", params, conn)

def handle_list(conn):
    """
    fetches a list of available topics
    conn(websocket): a valid connection to the echochat server
    """
    send_ws_request("LIST_TOPICS", {}, conn)

def handle_status(conn, name = ""):
    """
    gets the status of the given topic
    conn(websocket): a valid connection to the echochat server
    name(str): the topic check
    """
    topic = input("Choose topic to check:\n>> ") if name == "" else name
    send_ws_request("GET_TOPIC_STATUS", {"name": topic}, conn)

def end_loop(_):
    """ ends the interactive prompt """
    raise KeyboardInterrupt

def handle_input(command, conn):
    """
    handles user input from the command line
    command(str): the given user command
    conn(websocket): a valid websocket connection to the echochat server
    """
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
        functions[command.strip()](conn)
    except KeyError:
        # function not available
        print("invalid function")


def format_subscribe(resp):
    """
    formats a subscribe respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']
        lead = f"Subscribe @ {data['topic']}"
        sub =  f" -> Successfully subscribed to {data['topic']}"
        formatted = f"{lead}\n{sub}"
    else:
        formatted = "Subscribe request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted


def format_unsubscribe(resp):
    """
    formats a unsubscribe respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']
        lead = f"Unsubscribe @ {data['topic']}"
        sub =  f" -> Successfully unsubscribed from {data['topic']}"
        formatted = f"{lead}\n{sub}"
    else:
        formatted = "Unsubscribe request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted


def format_publish(resp):
    """
    formats a publish respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']

        lead = f"Publish @ {data['topic']} | Successful"
        sub = "Following message was published:"
        message = textwrap.fill(data['message'], width=52, initial_indent=" -> ", subsequent_indent="    ")

        formatted = f"{lead}\n{sub}\n{message}"
    else:
        formatted = "Publish request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted


def format_status(resp):
    """
    formats a topic status respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']

        lead =  f"Status @ {data['topic']} | {data['topic_status']}"
        info1 = f" -> Last Updated {data['last_update']}"
        info2 = f" -> Subscriber Count: {data['subscribers']}"
        
        formatted = f"{lead}\n{info1}\n{info2}"
    else:
        formatted = "Status request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted

    
def format_list(resp):
    """
    formats a list respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']

        lead = f"Topic List:"
        topics = ""
        for topic in data['topic_list']:
            topics += f"\n - {topic}"

        formatted = f"{lead}\n(no topics)" if topics == "" else f"{lead}{topics}"
    else:
        formatted = "List request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted
    
def format_update(resp):
    """
    formats an update respsonse
    data(dict): the json response
    """
    formatted = ""

    if resp['status'] == "success":
        data = resp['data']
        lead = f"Update @ {data['name']} | {data['timestamp'][11:16]}"
        message = textwrap.fill(data['message'], width=52, initial_indent="> ", subsequent_indent="  ")
        formatted = f"{lead}\n{message}"
    else:
        formatted = "Request unsuccessful!\n"
        formatted += f"Error: {resp['error']}"

    return formatted


def pretty_print_message(message):
    """
    formats the server response to be more human readable
    message(str): json response from the server
    """
    parsed = json.loads(message)

    functions = {
        "SUBSCRIBE_TOPIC": format_subscribe, 
        "UNSUBSCRIBE_TOPIC": format_unsubscribe, 
        "PUBLISH_TOPIC": format_publish, 
        "GET_TOPIC_STATUS": format_status, 
        "LIST_TOPICS": format_list,
        "UPDATE_TOPIC": format_update,
    }
    sep = "----------------------------------------------------"
    out = ""

    try:
        content = functions[parsed['function']](parsed)
        out = f"\n{sep}\n{content}\n{sep}\n> "
    except KeyError:
        # invalid function received
        pass
    
    return out
    


# adapted from https://stackoverflow.com/a/49899135
async def listener(conn):
    """
    the listener that receives messages from the websocket
    conn(websocket): a valid connection to the echochat server
    """
    try:
        while True:
            result = conn.recv()
            #print(f"\n{result}\n> ", end="")
            print(pretty_print_message(result), end="")
    except ConnectionClosedOK:
        #print("\nwebsocket closed")
        pass
    except ConnectionClosedError:
        #print("\nwebsocket died")
        pass
    except KeyboardInterrupt:
        pass

def start_thread(loop, conn):
    """
    starts a given event loop and passes a websocket connection
    loop(loop): an asyncio event loop
    conn(websocket): a valid connection to the echochat server
    """
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listener(conn))

def start_socket(conn):
    """
    creates an event loop and separate thread
    conn(websocket): a valid connection to the echochat server
    """
    worker_loop = asyncio.new_event_loop()
    worker = threading.Thread(target=start_thread, args=(worker_loop, conn))
    worker.start()
    return worker_loop

def do_args():
    """ sets up the args for the static CLI and parses them """
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
                        help="selects the output type, defaults to %(default)s")
    parser.add_argument("command",
                        nargs="?",
                        choices=["list", "status", "subscribe", "publish"],
                        help="the command to be run, either: list, status, subscribe, publish")
    parser.add_argument("topic",
                        nargs="?",
                        help="the topic parameter")
    parser.add_argument("message",
                        nargs="?",
                        help="the message to publish")
    return parser.parse_args()

def main():
    """ main control logic, entry point """

    # parse command line options
    args = do_args()

    # connect our client to the server
    uri = "ws://127.0.0.1:8000/ws"
    conn = connect(uri)

    if args.cli:
        # do command line actions
        if args.command == "list":
            handle_list(conn)
        elif args.command == "status":
            handle_status(conn, args.topic)
        elif args.command == "subscribe":
            handle_subscribe(conn, args.topic)
        elif args.command == "publish":
            handle_subscribe(conn, args.topic)
            handle_publish(conn, args.topic, args.message)

        if args.command in ("subscribe", "publish"):
            try:
                while True:
                    # wait for new messages
                    result = conn.recv()
                    print(result)
            except KeyboardInterrupt:
                conn.close()
        else:
            # wait for server response
            result = conn.recv()
            print(result)

            # exit
            conn.close()
            sys.exit(0)

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
