# EchoChat
A publisher-subscriber based chat system

## Dependencies
 - Python >=3.10
 - Uvicorn
 - Websockets
 - FastAPI

## Docs

The documentation for both the server and the clients is available in the file `documentation.pdf` (this documentation is in German, translation pending).

## Installation
This repository contains a Linux script for quickly starting this project.
To use this script, the packages `git`, `python3.10`, and `python-venv` needs to be available from the command line.
Then, the following commands can be used to start the server:

```
# Linux
apt-get install Python3.10 Python3.10-venv
git clone https://github.com/DHBW-FN-TIT20/EchoChat
cd EchoChat && ./start.sh
```

The EchoChat server can also be started manually with the following Python dependencies:

```sh
# Linux
pip3 install fastapi
pip3 install uvicorn
pip3 install websockets
pip3 install argparse

# Windows
pip install fastapi
pip install uvicorn
pip install websockets
pip install argparse

```
Alternatively, replace `pip3/pip` with `python -m pip install [package]`
Then, the server can be started by invoking `uvicorn` from the command line.

```sh
# Linux
cd EchoChat && uvicorn app:app

# Windows
cd EchoChat
uvicorn app:app
```
This should create a webserver available at [http://127.0.0.1:8000](http://127.0.0.1:8000)
Additionally, the repo also contains a Python CLI available under `./app/client.py`.
Usage information is available by calling `python client.py --help`.

