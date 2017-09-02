#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import http.client
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

import oauth2 as oauth

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_DIM = 16
TELLSTICK_UP = 128
TELLSTICK_DOWN = 256

RASPI_ID = 274164
SALON_ID = 223659
SAM_ID = 223659
NAS_ID = 274165

SUPPORTED_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_DIM | TELLSTICK_UP \
                    | TELLSTICK_DOWN


class Telldus:
    methods = {
        'ON': TELLSTICK_TURNON,
        'OFF': TELLSTICK_TURNOFF,
        'DIM': TELLSTICK_DIM,
        'UP': TELLSTICK_UP,
        'DOWN': TELLSTICK_DOWN,
        'BELL': TELLSTICK_BELL
    }
    
    states = {
        TELLSTICK_BELL: 'BELL',
        TELLSTICK_DOWN: 'DOWN',
        TELLSTICK_UP: 'UP',
        TELLSTICK_DIM: 'DIM',
        TELLSTICK_TURNOFF: 'OFF',
        TELLSTICK_TURNON: 'ON'
    }
    
    def __init__(self, tokens):
        self.private_key = tokens['private_key']
        self.public_key = tokens['public_key']
        self.token = tokens['token']
        self.token_secret = tokens['token_secret']
    
    def do_request(self, method, params):
        consumer = oauth.Consumer(self.public_key, self.private_key)
        token = oauth.Token(self.token, self.token_secret)
        
        oauth_request = oauth.Request.from_consumer_and_token(consumer, token=token, http_method='GET',
                                                              http_url="http://api.telldus.com/json/" + method,
                                                              parameters=params)
        oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
        headers = oauth_request.to_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        conn = http.client.HTTPConnection("api.telldus.com:80")
        conn.request('GET', "/json/" + method + "?" + urllib.parse.urlencode(params, True).replace('+', '%20'),
                     headers=headers)
        response = conn.getresponse().read().decode()

        return json.loads(response)
    
    def list_devices(self):
        response = self.do_request('devices/list', {'supportedMethods': SUPPORTED_METHODS})
        return response['device']
    
    def get_device_state(self, deviceID):
        response = self.do_request('device/info', {'id': deviceID, 'supportedMethods': 255})
        val = int(response['state'])
        val2 = str(response['statevalue'])
        
        if val in self.states:
            state = self.states[val]
        else:
            state = 'UNKNOWN'
        return state, val2
    
    def do_method(self, deviceId, methodId, methodValue=0):
        
        response = self.do_request('device/info', {'id': deviceId})
        
        method = ''
        if methodId == TELLSTICK_TURNON:
            method = 'on'
        elif methodId == TELLSTICK_TURNOFF:
            method = 'off'
        elif methodId == TELLSTICK_BELL:
            method = 'bell'
        elif methodId == TELLSTICK_UP:
            method = 'up'
        elif methodId == TELLSTICK_DOWN:
            method = 'down'
        elif methodId == TELLSTICK_DIM:
            method = 'dim'
        
        if 'error' in response:
            name = ''
            retString = response['error']
        else:
            name = response['name']
            response = self.do_request('device/command', {'id': deviceId, 'method': methodId, 'value': methodValue})
            if 'error' in response:
                retString = response['error']
            else:
                retString = response['status']
        
        if methodId in (TELLSTICK_TURNON, TELLSTICK_TURNOFF):
            print("Turning %s device %s, %s - %s" % (method, deviceId, name, retString))
            return retString
        elif methodId in (TELLSTICK_BELL, TELLSTICK_UP, TELLSTICK_DOWN):
            print("Sending %s to: %s %s - %s" % (method, deviceId, name, retString))
            return retString
        elif methodId == TELLSTICK_DIM:
            print("Dimming device: %s %s to %s - %s" % (deviceId, name, methodValue, retString))
            return retString
    
    def requestToken(self):
        
        consumer = oauth.Consumer(self.public_key, self.private_key)
        request = oauth.Request.from_consumer_and_token(consumer, http_url='http://api.telldus.com/oauth/requestToken')
        request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
        conn = http.client.HTTPConnection('api.telldus.com:80')
        conn.request(request.http_method, '/oauth/requestToken', headers=request.to_header())
        
        resp = conn.getresponse().read()
        token = oauth.Token.from_string(resp)
        print((
            'Open the following url in your webbrowser:\nhttp://api.telldus.com/oauth/authorize?oauth_token=%s\n'
            % token.key))
        print(('After logging in and accepting to use this application run:\n%s --authenticate' % (sys.argv[0])))
        self.token = str(token.key)
        self.token_secret = str(token.secret)
        return str(token.key), str(token.secret)
    
    def getAccessToken(self):
        consumer = oauth.Consumer(self.public_key, self.private_key)
        token = oauth.Token(None, None)
        request = oauth.Request.from_consumer_and_token(consumer, token=token, http_method='GET',
                                                        http_url='http://api.telldus.com/oauth/accessToken')
        request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
        conn = http.client.HTTPConnection('api.telldus.com:80')
        conn.request(request.http_method, request.to_url(), headers=request.to_header())
        
        resp = conn.getresponse()
        if resp.status != 200:
            print(('Error retrieving access token, the server replied:\n%s' % resp.read()))
            return
        token = oauth.Token.from_string(resp.read())
        
        self.token = str(token.key)
        self.token_secret = str(token.secret)
        print('Authentication successful, you can now use tdtool')
        return str(token.key), str(token.secret)


def authenticate(td):
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['authenticate'])
        for opt, arg in opts:
            if opt in '--authenticate':
                td.getAccessToken()
                return
    except getopt.GetoptError:
        pass
    td.requestToken()


def printUsage():
    print(("Usage: %s [ options ]" % sys.argv[0]))
    print("")
    print("Options:")
    print("         -[lnfdbvh] [ --list ] [ --help ]")
    print("                      [ --on device ] [ --off device ] [ --bell device ]")
    print("                      [ --dimlevel level --dim device ]")
    print("                      [ --up device --down device ]")
    print("")
    print("       --list (-l short option)")
    print("             List currently configured devices.")
    print("")
    print("       --help (-h short option)")
    print("             Shows this screen.")
    print("")
    print("       --on device (-n short option)")
    print("             Turns on device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --off device (-f short option)")
    print("             Turns off device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --dim device (-d short option)")
    print("             Dims device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("             Note: The dimlevel parameter must be set before using this option.")
    print("")
    print("       --dimlevel level (-v short option)")
    print("             Set dim level. 'level' should an integer, 0-255.")
    print("             Note: This parameter must be set before using dim.")
    print("")
    print("       --bell device (-b short option)")
    print("             Sends bell command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --up device")
    print("             Sends up command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --down device")
    print("             Sends down command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("Report bugs to <info.tech@telldus.se>")


def main(argv):
    tokens = {
        'private_key': 'a',
        'public_key': 'b',
        'token': 'c',
        'token_secret': 'd'
    }
    
    td = Telldus(tokens)
    
    try:
        opts, args = getopt.getopt(argv, "ln:f:d:b:v:h",
                                   ["list", "on=", "off=", "dim=", "bell=", "dimlevel=", "up=", "down=", "help"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    
    dimlevel = -1
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
        
        elif opt in ("-l", "--list"):
            print(json.dumps(td.list_devices(), indent=4))
            print(td.get_device_state('199137'))
        
        elif opt in ("-n", "--on"):
            td.do_method(arg, TELLSTICK_TURNON)
        
        elif opt in ("-f", "--off"):
            td.do_method(arg, TELLSTICK_TURNOFF)
        
        elif opt in ("-b", "--bell"):
            td.do_method(arg, TELLSTICK_BELL)
        
        elif opt in ("-d", "--dim"):
            if dimlevel < 0:
                print("Dimlevel must be set with --dimlevel before --dim")
            else:
                td.do_method(arg, TELLSTICK_DIM, dimlevel)
        
        elif opt in ("-v", "--dimlevel"):
            dimlevel = arg
        
        elif opt in "--up":
            td.do_method(arg, TELLSTICK_UP)
        
        elif opt in "--down":
            td.do_method(arg, TELLSTICK_DOWN)


if __name__ == "__main__":
    main(sys.argv[1:])
