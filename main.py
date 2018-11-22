from flask import Flask, render_template
from statistics import mean
import eventlet, socketio, time, math, random
timing = 0
done = 0
times = {}
time_array = [[] for _ in range(20)]
number_of_measurements = [0 for _ in range(20)]
time_avgs = {}

def startTime(num):
    global times
    times[num] = {'t0': time.time()}
def stopTime(num):
    global times
    times[num]['t1'] = time.time()
    times[num]['time'] = times[num]['t1'] - times[num]['t0']
    time_array[num].append(times[num]['time'])
    time_avgs[num] = mean(time_array[num])
    number_of_measurements[num] += 1

def randPrime(min, n):
    a = [False, False] + [True for _ in range(n - 1)]
    for i in range(2, math.floor(math.sqrt(n) + 1)):
        if a[i]:
            k = 0
            j = (i + k) * i
            while j <= n:
                a[j] = False
                k += 1
                j = (i + k) * i
    outlist = []
    for i in range(min, n + 1):
        if a[i]:
            outlist.append(i)
    print('generated')
    return random.choice(outlist)


users = {}
keys = {
    'p': random.randint(0, 1000000),
    'q': randPrime(0, 1000000)
}
user_names = {}
hashed_user_names = {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
app = Flask(__name__)
sio = socketio.Server()

@app.route('/')
def sessions():
    return render_template('session.html')

@sio.on('new user')
def new_user(sid, json, methods=['GET', 'POST']):
    print('new user. SID: ' + sid)
    users[sid] = True
    sio.emit('hash', {'hashes': list(hashed_user_names.values())}, room=sid)
    global timing
    if len(users) > 1: 
        timing = len(users)
        startTime(timing)
    if len(users) == 2:
        sio.emit('init', keys)
    elif len(users) > 2:
        sio.emit('use prev', {**keys, 'id': sid}, skip_sid=sid)
        sio.emit('init', keys, room=sid)

@sio.on('my hash')
def my_hash(sid, json, methods=['GET', 'POST']):
    hashed_user_names[sid] = json['myHash']


@sio.on('swap')
def swap(sid, json, methods=['GET', 'POST']):
    print(f"Swap. O: {json['a']}, P: {json['p']}, Q: {json['q']}")
    sio.emit('new o', json, skip_sid=sid)

@sio.on('big swap')
def big_swap(sid, json, methods=['GET', 'POST']):
    print('Big swap. O: ' + str(json['a']))
    sio.emit('new o', json, room=json['new_id'])

@sio.on('join')
def join(sid, json, methods=['GET', 'POST']):
    user_names[sid] = json['user_name']
    sio.emit('join', json, skip_sid=sid)
    global done, timing
    done += 1
    if done == timing:
        stopTime(timing)
        done = 0
        timing = 0
        print(f'Times: {time_avgs}, Measurements: {number_of_measurements[4]}')

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
    if sid in hashed_user_names:
        hashed_user_names.pop(sid)
    print(users)

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    print('started server')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)
