import socket
from time import sleep

from kodipydent import Kodi


def isLinuxUp(ip, port=22):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except socket.error:
        return False


def isWinUp(ip, port=0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.close()
        
        return True
    except socket.error:
        return False


def isKodiUp(ip, ntry=5):
    count = 1
    while count < ntry:
        try:
            k = Kodi(ip)
            k.JSONRPC.Version()
            return True
        except:
            sleep(1)
            count += 1
    return False


def stopKodi(ip):
    try:
        k = Kodi(ip)
        resp = k.System.Shutdown()
        sleep(15)
        return True
    except:
        return False
