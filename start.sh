mkdir ./venv
python3 -m venv ./venv
venv/bin/python -m pip install uvicorn
venv/bin/python -m pip install fastapi
venv/bin/python -m pip install websockets
venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
