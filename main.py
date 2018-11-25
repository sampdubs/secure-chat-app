# import dependencies
from flask import Flask, render_template
from statistics import mean
import eventlet, socketio, time, math, random
# set up variables for keeping track of what you're timing and how many times you have, etc.
timing = 0
done = 0
times = {}
time_array = [[] for _ in range(20)]
number_of_measurements = [0 for _ in range(20)]
time_avgs = {}

# functions for starting and stopping the timer
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

# a function that uses the Sieve of Eratosthenes to generate a random prime between two numbers
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
    return random.choice(outlist)

# dict to keep track of whether sids are connected
users = {}
# dict to keep track of public keys
keys = {
    'p': random.randint(100, 100000),
    'q': randPrime(100, 1000000)
}
# dict to keep track of sids mapping to encrypted usernames
user_names = {}
# dict to keep track of sids mapping to sha256 hashes of usernames
hashed_user_names = {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
# set up the server and socketio
app = Flask(__name__)
sio = socketio.Server()

# when a user connects, show session.html
@app.route('/')
def sessions():
    return render_template('session.html')

# when someone connects
@sio.on('new user')
def new_user(sid, json, methods=['GET', 'POST']):
    print('new user. SID: ' + sid)
    # remember that they are connected
    users[sid] = True
    # send back hashes of other users' usernames/ask for that user's hash
    sio.emit('hash', {'hashes': list(hashed_user_names.values())}, room=sid)
    # be able to use the timing variable
    global timing
    # if there are multiple users connected
    if len(users) > 1: 
        # remember how many users you are timing
        timing = len(users)
        # start the timer
        startTime(timing)
    # if there are exactly two users
    if len(users) == 2:
        # send the init message with the public keys
        sio.emit('init', keys)
    # if there are more than two users
    elif len(users) > 2:
        # send the use prev message to all but the newest user
        sio.emit('use prev', {**keys, 'id': sid}, skip_sid=sid)
        # send the init message along with the public keys to the newest user
        sio.emit('init', keys, room=sid)

# when a user sends back their sha256 hash
@sio.on('my hash')
def my_hash(sid, json, methods=['GET', 'POST']):
    # remember that their sid goes with that sha256 hash
    hashed_user_names[sid] = json['myHash']

# facilitates one user sending out their a value to everyone
@sio.on('swap')
def swap(sid, json, methods=['GET', 'POST']):
    print(f"Swap. A: {json['a']}, P: {json['p']}, Q: {json['q']}")
    sio.emit('new o', json, skip_sid=sid)

# facilitates multiple users sending out their a value to the newest user
@sio.on('big swap')
def big_swap(sid, json, methods=['GET', 'POST']):
    print('Big swap. A: ' + str(json['a']))
    sio.emit('new o', json, room=json['new_id'])

# once a user has arrived at the key
@sio.on('join')
def join(sid, json, methods=['GET', 'POST']):
    # uptate that their sid maps to their user name (encrypted with the key they just arrived at)
    user_names[sid] = json['user_name']
    # send out that they joined to everyone else
    sio.emit('join', json, skip_sid=sid)
    # be able to use timing variables
    global done, timing
    # increase the count of how many users have finnished the process
    done += 1
    # if all users are finished
    if done == timing:
        # stop the timer
        stopTime(timing)
        # reset variables
        done = 0
        timing = 0
        print(f'Times: {time_avgs}, Measurements: {number_of_measurements[2]}')

# facilitates sending out encrypted messages from one user to all users
@sio.on('msg')
def msg(sid, json, methods=['GET', 'POST']):
    print(f"When your message was sent, your username was sent as \n {json['user_name']} \nAnd your message was sent as \n {json['message']} \n")
    user_names[sid] = json['user_name']
    sio.emit('new msg', json)

# when a user disconnects
@sio.on('disconnect')
def disconnect(sid):
    print('someone disconnected: ' + sid)
    # if you have that sid's user name in memory (should always be True)
    if sid in user_names:
        # take that sid's user name out of memory
        users.pop(sid)
        # tell all other users that that user has left
        sio.emit('leave', {'user_name': user_names[sid]})
    # if you have that sid's hash in memory (should always be True)
    if sid in hashed_user_names:
        # take that sid's hash out of memory
        hashed_user_names.pop(sid)
    print(users)

# if this program is the main program running (should always be True)
if __name__ == '__main__':
    # initialize the app with flask and socketio
    app = socketio.Middleware(sio, app)
    print('started server')
    # start the server on localhost port 8080
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)