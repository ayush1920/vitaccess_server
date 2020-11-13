import socket
import time
import sys
import subprocess
import threading
from debug.serverlog import consoleLog, print_exc_plus
import debug.detector as exploitDetector
import maintenance.driveUpload as driveUpload
import telegram.bot as tgbot

HOST = '127.0.0.1'
PORT = 6969 

class maintain:
    def __init__(self):
        self.res = True
        self.inz = False
        self.resp = {"response":"error", "msg":"Maintance Mode", "code":23},503
    def on(self,response):
        self.res = True
        self.resp = response, 503
    def off(self):
        self.res = False
    def portStart(self):
        self.res = False
        self.inz = True

server =  maintain()

def shutdown(conn):
    conn.sendall(b"INITIATING SHUTDOWN PROCESS\n")
    mainOn(conn)

def shutdownTime(conn, Time):
    conn.sendall(b"INITIATING SHUTDOWN PROCESS\n")
    mainOn(conn, Time)

def mainOn(conn, Time = False):
    conn.sendall(b"INITIATING MAINTAINANCE SWITCH\n")
    if Time:
        server.on({"response":"error", "msg":f"Maintance Mode Enabled. End Time:{Time}", "code":24})
    else:
        server.on({"response":"error", "msg":"Maintance Mode", "code":23})
    time.sleep(1)
    # Flush data from exploit logs.
    exploitDetector.flushLogs()
    conn.sendall(bytes(f'{"TIMED " if Time else ""}MAINTENANCE MODE ON,succ\n','utf-8'))    

def mainOff(conn):
    conn.sendall(b"INITIATING MAINTAINANCE SWITCH\n")
    server.off()
    time.sleep(1)
    conn.sendall(b'MAINTENANCE MODE OFF,succ\n')   

def backup(conn):
    driveUpload.backup()
    server.off()
    time.sleep(1)
    tgbot.bot.send_message(str('SERVER ONLINE')) 
    
    
def initialise():
    try:
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                server.portStart()
                s.listen(1)
                conn, addr = s.accept()
                with conn:
                    while True:
                        time.sleep(1)
                        data = conn.recv(1024)
                        if data:
                            command = data.decode('utf-8')
                            break
                    conn.sendall(bytes(f'Started Executing command - {command}\n','utf-8'))
                    command = command.split('_')
                    cmn = command[0]
                    if cmn =="10":
                        shutdownTime(conn, command[-1])
                    elif cmn == "20":
                        shutdown(conn)
                    elif cmn == '30':
                        mainOn(conn, command[-1])
                    elif cmn == '40':
                        mainOn(conn)
                    elif cmn == '50':
                        mainOff(conn)
                    elif cmn == '60':
                        backup(conn)
                    elif cmn == '80':
                        conn.sendall(b'PORT IS ALIVE,succ\n')        
                    elif cmn == '100':
                        server.inz = False
                        conn.sendall(b'KILLPORT BEFORE INITIATE\n')
                        sys.exit()
                    else:
                        conn.sendall(b"NO COMMAND FOUND_EXIT\n")
                    conn.close()
    except:
        print_exc_plus(mod =3, force = True, exceptionData = sys.exc_info())
        server.inz=False
        start()
        sys.exit()
        
def start():
    if server.inz:
        return
    threading.Thread(target =  initialise, daemon=True).start()
    while True:
        time.sleep(.4)
        if server.inz:break
    
