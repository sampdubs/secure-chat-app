from flask import Flask, render_template
import eventlet
import socketio
from apscheduler.schedulers.background import BackgroundScheduler
from time import time
from json import loads

users = {}
keys = {}
user_names = {}

app = Flask(__name__)
sio = socketio.Server()

@app.route('/')
def sessions():
    if len(users) < 2:
        return render_template('session.html')
    return "sorry only 2 users allowed for now..."

@sio.on('new user')
def new_user(sid, json, methods=['GET', 'POST']):
    print('new user. ID: ' + sid)
    users[sid] = True
    keys['p'] = json['p']
    keys['q'] = json['q']
    print(users)
    sio.emit('init', json);
    
@sio.on('swap')
def swap(sid, json, methods=['GET', 'POST']):
    print('Swap. O: ' + str(json['a']))
    sio.emit('new o', json, skip_sid=sid);

@sio.on('msg')
def handle_my_custom_event(sid, json, methods=['GET', 'POST']):
    print('received msg: ' + str(json))
    user_names[sid] = json['user_name']
    sio.emit('new msg', json)

@sio.on('disconnect')
def disconnect(sid):
    print('someone disconnected: ' + sid)
    users.pop(sid)
    sio.emit('leave', {'user_name': user_names[sid]})
    sio.emit('init', keys);
    

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    print('started server')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)