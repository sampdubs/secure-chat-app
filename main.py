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
    return render_template('session.html')

@sio.on('new user')
def new_user(sid, json, methods=['GET', 'POST']):
    print('new user. ID: ' + sid)
    users[sid] = True
    if len(users) == 2:
        sio.emit('init', json)
        keys['p'] = json['p']
        keys['q'] = json['q']
    elif len(users) > 2:
        sio.emit('use prev', {**json, 'id': sid}, skip_sid=sid)
        sio.emit('init', keys, room=sid)
    
@sio.on('swap')
def swap(sid, json, methods=['GET', 'POST']):
    print('Swap. O: ' + str(json['a'])) 
    sio.emit('new o', json, skip_sid=sid)

@sio.on('big swap')
def big_swap(sid, json, methods=['GET', 'POST']):
    print('Big swap. O: ' + str(json['a']))
    sio.emit('new o', json, room=json['new_id'])

@sio.on('msg')
def handle_my_custom_event(sid, json, methods=['GET', 'POST']):
    print('received msg: ' + str(json))
    user_names[sid] = json['user_name']
    sio.emit('new msg', json)

@sio.on('disconnect')
def disconnect(sid):
    print('someone disconnected: ' + sid)
    if sid in user_names:
        users.pop(sid)
        sio.emit('leave', {'user_name': user_names[sid]})
    print(users)
    

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    print('started server')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)