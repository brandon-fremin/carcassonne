from flask import Flask  # Import flask
from flask import request as FlaskRequest
import random, traceback
from handle_get_state import handle_get_state
from handle_new_game import handle_new_game
from handle_place_tile import handle_place_tile
from time import sleep

SERVER_PORT = 8080

app = Flask(__name__)  # Setup the flask app by creating an instance of Flask

def middleware(func):
    def wrapper(*args, **kwargs):
        try:
            print(func.__name__)
            request = FlaskRequest.json
            print(request, flush=True)
            response = func(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            print(e)
            response = {"error": tb}
        print("Response", response, flush=True)
        return response
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/hello')  # When someone goes to / on the server, execute the following function
@middleware
def hello():
    response = {
        "hello": "world"
    }  # Return this message back to the browser
    return response

@app.route('/getState', methods=["GET", "PUT"])
@middleware
def getState():
    request = FlaskRequest.json
    response = handle_get_state(request)
    return response

@app.route('/newGame', methods=["GET", "PUT"])
@middleware
def newGame():
    request = FlaskRequest.json
    response = handle_new_game(request)
    return response

@app.route('/placeTile', methods=["GET", "PUT"])
@middleware
def placeTile():
    request = FlaskRequest.json
    response = handle_place_tile(request)
    return response

@app.route('/poll', methods=["GET", "PUT"])
@middleware
def poll():
    request = FlaskRequest.json
    print(request, flush=True)
    sleep(15)
    response = {
        "data": f"Random Number: {random.random()}"
    }
    print(response, flush=True)
    return response

if __name__ == '__main__':  # If the script that was run is this script (we have not been imported)
    app.run(port=SERVER_PORT, debug=True)  # Start the server