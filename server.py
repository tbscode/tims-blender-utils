from flask import Flask, request
from gevent.pywsgi import WSGIServer
import subprocess
from telegram.client import Telegram
from threading import Thread
import requests
import os
import flask

app = Flask(__name__)
from flask import g


TASKS = []
def init_app():
    print("Blender server started")

def start_server():
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()

@app.route("/", methods=['GET', 'POST'])
def index():
    return "Index Page"

@app.route("/tasks/", methods=['GET', 'POST'])
def tasks():
    global TASKS
    if flask.request.method == 'POST':
        new_task = flask.request.json["task"]
        TASKS.append(new_task)
    else:
        cur_tasks = flask.jsonify(TASKS)
        del TASKS[:]
        return cur_tasks

if __name__ == '__main__':
    Thread(target=start_server).start()
    with app.app_context():
        init_app()