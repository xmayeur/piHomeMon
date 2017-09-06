# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for
# from flask_security import login_required, logout_user, current_user
from flask_socketio import emit

# import fabric
import config
from app import app, tdtool, socketio, ndtool

# from flask_login import LoginManager

nodes = [
    {'id': 1, 'name': 'Média chambre', 'ip': '192.168.0.20', 'state': 0, 'value': 0, 'type': 'kodi', 'device': '199137',
     'img': ''},
    {'id': 2, 'name': 'Média salon', 'ip': '192.168.0.13', 'state': 0, 'value': 0, 'type': 'kodi', 'device': '274164',
     'img': ''},
    {'id': 3, 'name': 'Monitoring', 'ip': '192.168.0.12', 'state': 0, 'value': 0, 'type': 'rpi', 'device': '',
     'img': ''},
    {'id': 4, 'name': 'NAS', 'ip': '192.168.0.16', 'state': 0, 'value': 0, 'type': 'nas', 'device': '274165',
     'img': ''},
    {'id': 5, 'name': 'Webcam 1er', 'ip': '192.168.0.11', 'state': 0, 'value': 0, 'type': 'rpi', 'device': '',
     'img': ''},
    {'id': 8, 'name': 'bigTower', 'ip': '192.168.0.10', 'state': 0, 'value': 0, 'type': 'win', 'device': '', 'img': ''},
    {'id': 6, 'name': 'TV', 'ip': '', 'state': 0, 'value': 0, 'type': 'sw', 'device': '274166', 'img': ''},
    {'id': 7, 'name': 'Lampe SaM', 'ip': '', 'state': 0, 'value': 0, 'type': 'dim', 'device': '223659', 'img': ''}
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


def update_nodes(_nodes):
    for n in _nodes:
        if n['device'] != '':
            _state, _val = td.get_device_state(n['device'])
            n['state'] = methods[_state]
            try:
                value = int(int(_val) * 100 / 256)
                value = 0 if value < 5 else 100 if value > 95 else value
    
                n['value'] = str(value)
                if n['state'] == methods['ON']:
                    n['value'] = '100'
            except:
                n['value'] = 0 if n['state'] == methods['OFF'] else '100'
                n['state'] = methods['DIM']
                # print('device %s is %s - val %s' % (n['device'], n['state'], _val))

        else:
            # if no device is associated with the node, we have a always 'ON' state
            n['state'] = methods['ON']

        if n['state'] != methods['OFF']:
            if n['state'] == methods['BOOT'] or n['state'] == methods['SHUT']:
                continue
    
            elif n['type'] == 'kodi' or n['type'] == 'rpi' or n['type'] == 'nas':
                n['state'] = methods['ON'] if ndtool.isLinuxUp(n['ip']) else methods['UNKNOWN']
    
            elif n['type'] == 'win':
                n['state'] = methods['ON'] if ndtool.isWinUp(n['ip']) else methods['UNKNOWN']
    
            if n['type'] == 'kodi':
                n['state'] = methods['ON'] if ndtool.isKodiUp(n['ip']) else methods['UNKNOWN']
    
            if n['state'] == methods['UNKNOWN'] and n['device'] == '':
                n['img'] = url_for('static', filename='unknown' + '.png')
            else:
                n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
                # print('node %s is %s' % (n['name'], n['state']))
    return _nodes


@app.route('/')
# @login_required
def home():
    return redirect(url_for('do_devices'))


@app.route('/devices')
# @login_required
def do_devices():
    global nodes
    global states
    global devices

    # nickname = current_user.nickname
    nickname = 'Xavier'
    nodes = update_nodes(nodes)
    # print('nodes refreshed')
    return render_template('index.html', nodes=nodes, states=states, nickname=nickname)


@socketio.on('refresh')
def refresh(msg):
    global nodes
    global devices
    global states

    # devices = td.list_devices()
    # update page objects in function of states
    # refresh node's states in function of devices states
    nodes = update_nodes(nodes)
    
    for n in nodes:
        if n['state'] == 0:
            n['img'] = url_for('static', filename='unknown' + '.png')
        elif n['state'] == methods['BOOT'] or n['state'] == methods['SHUT']:
            continue
        elif n['state'] == methods['DIM']:
            emit('setSlider', {'value': n['value']})
        else:
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
        
        emit('refreshResponse', {
            'pict': n['img'],
            'alt': n['name']
        })
        emit('reactivateImg', {'alt': n['name']})


@socketio.on('clickEvent')
def imgclick(msg):
    global td

    print('click on %s' % msg['name'])
    n = nodes[indexes[msg['name']]]
    
    if n['state'] == methods['OFF']:
        if n['device'] != '':
            td.do_method(n['device'], methods['ON'])
            n['state'] = methods['ON']
        if n['type'] == 'kodi':
            print('Booting up Kodi')
            n['state'] = methods['BOOT']
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
            emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
            n['state'] = methods['ON'] if ndtool.isKodiUp(n['ip']) else methods['OFF']
            print('kodi state: %s' % states[n['state']])
        elif n['type'] == 'rpi':
            n['state'] = methods['ON'] if ndtool.isLinuxUp(n['ip']) else methods['OFF']
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
            emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
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
            ndtool.stopKodi(n['ip'])
        elif n['type'] == 'rpi':
            n['state'] = methods['ON'] if ndtool.isLinuxUp(n['ip']) else methods['OFF']
            n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
            emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
        elif n['type'] == 'nas':
            # send a shutdown action and wait for 5 min
            emit('reactivateImg', {'alt': n['name']})
            return
        elif n['type'] == "win":
            pass
        else:
            pass
        if n['device'] != '':
            td.do_method(n['device'], methods['OFF'])
            n['state'] = methods['OFF']
    
    n['img'] = url_for('static', filename=n['type'] + states[n['state']] + '.png')
    emit('refreshResponse', {'pict': n['img'], 'alt': n['name']})
    emit('reactivateImg', {'alt': n['name']})


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    
    return decorate


@static_vars(busy=False)
@socketio.on('getSlider')
def getDimmer(msg):
    if getDimmer.busy:
        return
    getDimmer.busy = True
    value = int(int(msg['value']) * 256 / 100)
    value = 0 if value < 5 else 100 if value > 95 else value
    print('%s - set to value %s' % (msg['name'], msg['value']))
    
    if value == 0:
        td.do_method(n['device'], methods['OFF'])
    elif value == 256:
        td.do_method(n['device'], methods['ON'])
    else:
        td.do_method(n['device'], methods['DIM'], value)
    
    getDimmer.busy = False
    

@app.route('/webcams')
# @login_required
def webcams():
    return render_template('index.html')


@app.route('/logout')
def logout():
    # if current_user.is_authenticated:
    #     nickname = current_user.nickname
    #     logout_user()
    #     return 'Bye ' + nickname + '!'
    # else:
    #     return 'Bye!'
    return 'Bye'


"""
@app.route('/login')
def login():
    login_user(models.User)
    redirect(url_for('/'))
"""
