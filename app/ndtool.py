import socket
from errno import ECONNREFUSED
from time import sleep

from kodipydent import Kodi


def isLinuxUp(ip, port=22):
    return portscan(ip, port)


def isWinUp(ip, port=139):
    return portscan(ip, port)


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


def portscan(target, port):
    try:
        # Create Socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketTimeout = 5
        s.settimeout(socketTimeout)
        s.connect((target, port))
        # print(('port_scanner.is_port_opened() ' + str(port) + " is opened"))
        return port
    except socket.error as err:
        if err.errno == ECONNREFUSED:
            return False
