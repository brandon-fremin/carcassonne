from flask_socketio import SocketIO, emit
from flask import Flask
import os

APP = Flask(__name__)

# configure cors_allowed_origins
if os.environ.get('FLASK_ENV') == 'production':
    origins = [
        'http://actual-app-url.herokuapp.com',
        'https://actual-app-url.herokuapp.com'
    ]
else:
    origins = "*"

# initialize your socket instance
socketio = SocketIO(cors_allowed_origins=origins)

# handle chat messages
@socketio.on("chat")
def handle_chat(data):
    emit("chat", data, broadcast=True)

# initialize the app with the socket instance
# you could include this line right after Migrate(app, db)
socketio.init_app(APP)

# at the bottom of the file, use this to run the app
if __name__ == '__main__':
    socketio.run(APP)


# import eventlet
# import socketio

# sio = socketio.Server(cors_allowed_origins=['*'])
# app = socketio.WSGIApp(sio, static_files={
#     '/': {'content_type': 'text/html', 'filename': 'index.html'}
# })

# @sio.event
# def connect(sid, environ):
#     print('connect ', sid)

# @sio.event
# def my_message(sid, data):
#     print('message ', data)

# @sio.event
# def disconnect(sid):
#     print('disconnect ', sid)

# if __name__ == '__main__':
#     eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

# import asyncio
# from websockets.server import serve, WebSocketServerProtocol

# async def echo(websocket: WebSocketServerProtocol):
#     async for message in websocket:
#         print(message, flush=True)
#         await websocket.send(message)

# async def main():
#     print("Serving...", flush=True)
#     async with serve(echo, "localhost", 5000, origins=["*"]):
#         await asyncio.Future()  # run forever

# asyncio.run(main())