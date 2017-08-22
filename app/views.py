from time import sleep

from flask import render_template, redirect, url_for
from flask_security import login_required, logout_user, current_user
from flask_socketio import emit
# import fabric
from kodipydent import Kodi

import config
from app import app, tdtool, socketio

nodes = [
    {'id': 1, 'name': 'Média chambre', 'ip': '192.168.0.20', 'state': 0, 'type': 'kodi', 'device': '199137', 'img': ''},
    {'id': 2, 'name': 'Média salon', 'ip': '192.168.0.13', 'state': 0, 'type': 'kodi', 'device': '274164', 'img': ''},
    {'id': 3, 'name': 'Monitoring', 'ip': '192.168.0.12', 'state': 0, 'type': 'rpi', 'device': '', 'img': ''},
    {'id': 4, 'name': 'NAS', 'ip': '192.168.0.16', 'state': 0, 'type': 'nas', 'device': '274165', 'img': ''},
    {'id': 5, 'name': 'Webcam 1er', 'ip': '192.168.0.11', 'state': 0, 'type': 'rpi', 'device': '', 'img': ''},
    {'id': 8, 'name': 'bigTower', 'ip': '192.168.0.10', 'state': 0, 'type': 'win', 'device': '', 'img': ''},
    {'id': 6, 'name': 'TV', 'ip': '', 'state': 0, 'type': 'sw', 'device': '274166', 'img': ''},
    {'id': 7, 'name': 'Eclairage SaM', 'ip': '', 'state': 0, 'type': 'sw', 'device': '223659', 'img': ''}
]

indexes = {}
i = 0
for n in nodes:
    indexes[n['name']] = i
    i += 1

td = tdtool.Telldus(config.tokens)
# device [] - {'id': int, 'name': str, 'state': int, ... }
devices = td.list_devices()
methods = td.methods
states = td.states
# enhance methods & states for nodes
methods['BOOT'] = 512
methods['SHUT'] = 1024
methods['UNKNOWN'] = 0
states[0] = 'UNKNOWN'
states[512] = 'BOOT'
states[1024] = 'SHUT'


def update_nodes(_nodes, _devices):
    for n in _nodes:
        for d in _devices:
            if n['device'] == d['id']:
                if d['state'] == tdtool.TELLSTICK_TURNOFF:
                    n['state'] = d['state']
                else:
                    # need more details of node state - need to probe node according to type
                    n['state'] = d['state']
                break
            else:
                # need more details of node state - need to probe node according to type
                n['state'] = methods['UNKNOWN']
    return _nodes


def getKodiState(_node):
    if _node['type'] != 'kodi':
        return
    max = 10
    count = 1
    resp = None
    while count < max:
        try:
            k = Kodi(_node['ip'])
            resp = k.JSONRPC.Version()
            print(resp)
            return 'ON'
        except Exception as e:
            sleep(1)
            count += 1
    return 'OFF'


def stopKodi(_node):
    if _node['type'] != 'kodi':
        return
    try:
        k = Kodi(_node['ip'])
        resp = k.System.Shutdown()
        sleep(15)
        return 'OFF'
    except:
        return 'UNKNOWN'


@app.route('/')
@login_required
def home():
    return redirect(url_for('do_devices'))


@app.route('/devices')
@login_required
def do_devices():
    global nodes
    global states
    global devices
    
    nickname = current_user.nickname
    devices = td.list_devices()
    nodes = update_nodes(nodes, devices)
    return render_template('index.html', nodes=nodes, states=states, nickname=nickname)


@socketio.on('refresh')
def refresh(msg):
    global nodes
    global devices
    global states
    
    devices = td.list_devices()
    
    # update page objects in function of states
    # refresh node's states in function of devices states
    nodes = update_nodes(nodes, devices)
    # print(devices)
    # print(nodes)
    # print associate the related icons
    for n in nodes:
        if n['state'] == 0:
            n['img'] = url_for('static', filename='unknown' + '.png')
        elif n['state'] == methods['BOOT'] or n['state'] == methods['SHUT']:
            continue
        else:
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
        
        emit('refreshResponse', {
            'pict': n['img'],
            'alt': n['name']
        })


@socketio.on('clickEvent')
def imgclick(msg):
    global td
    
    n = nodes[indexes[msg['name']]]
    
    if n['state'] == methods['OFF']:
        td.do_method(n['device'], methods['ON'])
        n['state'] = methods['ON']
        if n['type'] == 'kodi':
            print('Booting up Kodi')
            n['state'] = methods['BOOT']
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
            emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
        elif n['type'] == 'rpi':
            pass
        elif n['type'] == 'nas':
            pass
        elif n['type'] == "win":
            pass
        else:
            pass
    
    
    else:
        if n['type'] == 'kodi':
            print('Shutting down Kodi')
            n['state'] = methods['SHUT']
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
            emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
            stopKodi(n)
        elif n['type'] == 'rpi':
            pass
        elif n['type'] == 'nas':
            pass
        elif n['type'] == "win":
            pass
        else:
            pass
        td.do_method(n['device'], methods['OFF'])
        n['state'] = methods['OFF']
    
    n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
    emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})


@app.route('/webcams')
@login_required
def webcams():
    return render_template('index.html')


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        nickname = current_user.nickname
        logout_user()
        return 'Bye ' + nickname + '!'
    else:
        return 'Bye!'


"""
@app.route('/login')
def login():
    login_user(models.User)
    redirect(url_for('/'))
"""
