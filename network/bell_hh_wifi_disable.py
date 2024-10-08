#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python3 version of Avernar's (dslreports.com) HH4K/GH wifi script
# https://discord.com/channels/886329492438671420/886464327366881332/1054113813743550475

from collections import OrderedDict
from urllib.parse import urlencode
import random
import hashlib
import http.client
import json
import getopt
import sys
  
host = "192.168.2.1"
username = "admin"
password = "admin"
state = None
type = 0

argument_list = sys.argv[1:]
short_options = "?h:u:p:"
long_options = ["help", "host=", "user=", "pass=", "hh", "gh"]

def Usage():
    print("wifi.py [options] on|off")
    print("")
    print("type:")
    print("--hh: Home Hub 4000")
    print("--gh: Giga Hub")
    print("")
    print("options:")
    print("-?, --help: Help")
    print("-h {host}, --host {host}: Host name or IP.  Default: 192.168.2.1")
    print("-u {username}, --user {username}, --username {username}: User name or IP.  Default: admin")
    print("-p {password}, --pass {password}, --password {password}: Password.  Default: admin")

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
    print((str(err)))
    sys.exit(2)

if len(values) < 1:
    arguments = [('--help', '')]
else:
    param = values[0].lower()
    if param in ['on', 'enable', 'true']:
        state = True
    elif param in ['off', 'disable', 'false']:
        state = False
    else:
        arguments = [('--help', '')]

for current_argument, current_value in arguments:
    if current_argument in ("-?", "--help"):
        Usage()
        sys.exit(0)
    elif current_argument in ("-h", "--host"):
        host = current_value
    elif current_argument in ("-u", "--user", "--username"):
        username = current_value
    elif current_argument in ("-p", "--pass", "--password"):
        password = current_value
    elif current_argument in ("--hh"):
        type = 1
    elif current_argument in ("--gh"):
        type = 2

if type == 0:
    print("Router type required.")
    print("")
    Usage()
    sys.exit(3)

def MD5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def SHA512(s):
    return hashlib.sha512(s.encode("utf-8")).hexdigest()

def Hash(s, type):
    if type == 1:
        return MD5(s)
    if type == 2:
        return SHA512(s)
    return ""

def GetLocalNonce():
    random.seed()
    return random.randint(0, 4294967295)

def CalcHa1(user, password, type, nonce):
    return Hash("{0}:{1}:{2}".format(user, nonce, Hash(password, type)), type)

def CalcAuthKey(session, cNonce):
    ha1 = CalcHa1(session['username'], session['password'], session['type'], session['serverNonce'])
    return Hash("{0}:{1}:{2}:JSON:/cgi/json-req".format(ha1, session['requestID'], cNonce), session['type'])

def Post(host, req):
    outData = { "req": json.dumps(req) }
    headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    conn = http.client.HTTPConnection(host)
    conn.request("POST", "/cgi/json-req", urlencode(outData), headers)
    response = conn.getresponse()
    inData = response.read()
    return json.loads(inData)

def OpenSession(host, username, password, type):
    session = {
        'host': host,
        'username': username,
        'password': password,
        'type': type,
        'sessionID': 0,
        'requestID': 0,
        'serverNonce': ""
    }
    
    localNonce = GetLocalNonce()
  
    req = {
        "request": OrderedDict([
            ("id", session['requestID']),
            ("session-id", str(session['sessionID'])), # must be string
            ("priority", True),
            ("actions", [
                OrderedDict([
                    ("id", 0),
                    ("method", "logIn"),
                    ("parameters", OrderedDict([ 
                        ("user",  session['username']),
                        ("persistent", "true"), # must be string
                        ("session-options", OrderedDict([
                            ("nss", [
                                OrderedDict([
                                    ("name", "gtw"),
                                    ("uri", "http://sagemcom.com/gateway-data")
                                ])
                            ]),
                            ("language", "ident"),
                            ("context-flags", OrderedDict([
                                ("get-content-name", True),     # default True
                                ("local-time", True),           # default True
                                ("no-default", True)            # default False
                            ])),
                            ("capability-depth", 0),            # default 2
                            ("capability-flags", OrderedDict([
                                ("name", False),                # default True
                                ("default-value", False),       # default True
                                ("restriction", False),         # default True
                                ("description", False)          # default False
                            ])),
                            ("time-format", "ISO_8601"),
                            ("compatibility-flags", OrderedDict([
                                ("flags", False),               # default True
                                ("default-value", False),       # default True
                                ("type", False)                 # default True
                            ])),                            
                            ("depth", 99),                       # default 2, 6 = refresh, 99 = debug
                            ("write-only-string", "_XMO_WRITE_ONLY_"),
                            ("undefined-write-only-string", "_XMO_UNDEFINED_WRITE_ONLY_")
                        ]))
                    ]))
                ])
            ]),
            ("cnonce", localNonce),
            ("auth-key", CalcAuthKey(session, localNonce))
        ])
    }
  
    response = Post(session['host'], req)
     
    action = response["reply"]["actions"][0]
    if action["error"]["code"] != 16777238:
        if action["error"]["code"] == 16777223:
            print("Authentication Error")
        else:
            print((action["error"]["description"]))
        return None
     
    parameters = action["callbacks"][0]["parameters"]
  
    session['sessionID'] = int(parameters["id"])
    session['serverNonce'] = str(parameters["nonce"])
    session['requestID'] += 1
  
    return session
  
def SendActions(session, actions):
    localNonce = GetLocalNonce()
  
    req = {
        "request": OrderedDict([
            ("id", session['requestID']),
            ("session-id", session['sessionID']),
            ("priority", False),
            ("actions", actions),
            ("cnonce", localNonce),
            ("auth-key", CalcAuthKey(session, localNonce))
        ])
    }
  
    session['requestID'] += 1
  
    return Post(session['host'], req)
  
def SSID_AP(session, state):
    actions = [
        OrderedDict([
            ("id", 0),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/SSIDs/SSID[@uid='1']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 1),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/AccessPoints/AccessPoint[@uid='1']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 2),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/SSIDs/SSID[@uid='3']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 3),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/AccessPoints/AccessPoint[@uid='3']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 4),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/SSIDs/SSID[@uid='6']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 5),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/AccessPoints/AccessPoint[@uid='6']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 6),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/SSIDs/SSID[@uid='5']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 7),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/AccessPoints/AccessPoint[@uid='5']/Enable"),
            ("parameters", {
                "value": state
            })
        ])
    ]
  
    return SendActions(session, actions)
  
def Radios(session, state):
    actions = [
        OrderedDict([
            ("id", 0),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/Radios/Radio[@uid='1']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 1),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/Radios/Radio[@uid='2']/Enable"),
            ("parameters", {
                "value": state
            })
        ]),
        OrderedDict([
            ("id", 2),
            ("method", "setValue"),
            ("xpath", "Device/WiFi/Radios/Radio[@uid='3']/Enable"),
            ("parameters", {
                "value": state
            })
        ])
    ]
  
    return SendActions(session, actions)
  
session = OpenSession(host, username, password, type)
if not session:
    sys.exit(1)
  
SSID_AP(session, state)
Radios(session, state)
