from flask import Flask, render_template
import eventlet
import socketio
#from ast import literal_eval as array

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

@sio.on('join')
def join(sid, json, methods=['GET', 'POST']):
    user_names[sid] = json['user_name']
    sio.emit('join', json, skip_sid=sid)

@sio.on('msg')
def msg(sid, json, methods=['GET', 'POST']):
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

#f = open('/home/ec2-user/environment/aws.cloud.9/static/primes.txt', 'r')
#primes = f.read()
#primes = list(array(primes))
#print(len(primes))



if __name__ == '__main__':
    
    app = socketio.Middleware(sio, app)
    print('started server')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)