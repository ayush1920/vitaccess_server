#!/usr/bin/env python3

import socket
import time
import requests as rq
import sys
import os
from datetime import datetime
import threading
import traceback
import errno


HOST = '127.0.0.1'
PORT = 6969 

commandList = ["SHUTDOWN", 'MAIN-ON', 'MAIN-OFF', 'BACKUP', 'KILLPORT', 'STATUS']

instructions=f"""COMMANDS - {str(commandList)}

SHUTDOWN_TIME   - USE UNDERSCORE AND TIME TO TRIGGER MAINTAINACE WITH TIME.
MAIN-ON_TIME    - STARTS MAINTENANCE MODE
MAIN-OFF        - KILLS MAINTENANCE MODE
BACKUP          - CREATE AND PUSH CURRENT BACKUP OF CURRENT APP STATE. ENABLES MAINTENANCE
KILLPORT        - STOP THE SERVER PORT ON THE WEBAPP
STATUS          - CAN BE USED TO KNOW WHETHER PORT IS OPEN OR NOT, IN THE APP.

ENTER YOUR CHOICE
: """


def getDebugData():
    def appendData(initial, data):
        return initial + data +'\n'

    exc = sys.exc_info()
    deb = '-'*20
    deb = appendData(deb, str(datetime.now())+'-'*20)
    deb = appendData(deb, 'Error:\n'+''.join(traceback.format_exception(*exc)))
    #tb = sys.exc_info()[2]
    tb = exc[2]
    stack = []
    while True:
        stack.append(tb.tb_frame)
        tb = tb.tb_next
        if not tb:
            break
    deb = appendData(deb,'DEBUG DATA:')
    stack.reverse()
    for f in stack:
##      if str(f.f_code.co_name) == '<module>':
##          break
        deb = appendData(deb, f'Frame {f.f_code.co_name} in {f.f_code.co_filename} at line {f.f_lineno}')
        for key, value in f.f_locals.items():

            # does not logs password
            #if key == 'password': continue
            deb += f"\t\t{key} = "
            try:                   
                deb = appendData(deb, str(value))
            except:
                deb = appendData(deb, "<ERROR WHILE PRINTING VALUE>")
    return deb

#-------------------
# SERVER
#-------------------
PORT2 = 42069

def startServer():
    print('SERVER STARTED')
    try:
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT2))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    while True:
                        time.sleep(1)
                        data = conn.recv(1024)
                        if data:
                            command = data.decode('utf-8')
                            break
                    conn.sendall(bytes(f'Started Executing command - {command}\n','utf-8'))
                    commandManager(command)
                    conn.close()
    except:
        deb = getDebugData()
        with open('logs/maintenance/error.log','a+') as f:
            f.write(deb)
        msgAction(deb, True)
        

# ---------------------------------------------------------------------------------
def startSocket(isTgmcmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        return s
    except socket.error as error:
        if error.errno == errno.ECONNREFUSED:
            msgAction('PORT NOT OPEN',isTgmcmd)
        raise Exception('SOME ERROR OCCURED')  

def clear(): 
    if os.name == 'nt': 
        os.system('cls') 
    else: 
        os.system('clear')
        
def processData(data,isTgmcmd):
    if data:
        msgAction(data.decode('utf-8'),isTgmcmd)
        data= data.decode('utf-8').split(',')
        return data
    return []

def fetchdata_loop(s,isTgmcmd):
    cnt=0
    while True:
        cnt+=1
        time.sleep(1)
        data = processData(s.recv(1024),isTgmcmd)
        if data == [] and cnt<30:continue
        if cnt>=30:
            return False
        if data[-1] =='succ\n':
            return True

def sleepTime(Time, isTgmcmd = False):
    msgAction(f'INITIATING {Time} SEC SLEEP', isTgmcmd)
    for dec in range(Time,0,-1):
        print(f'Time remaining {dec} sec',end='\r')
        time.sleep(1)
        
def msgAction(msg,isTgmcmd = False, end='\n'):
    if isTgmcmd:
        url = f"https://api.telegram.org/bot1152939742:<TelegramAPI>/sendMessage?chat_id=<chat_id>&text={msg}"
        res = rq.get(url)
    else:
        print(msg,end=end)

def shutdown(command, isTgmcmd):
    s = startSocket(isTgmcmd)
    s.sendall(command)
    loop_success = fetchdata_loop(s, isTgmcmd)
    if not loop_success:
        msgAction('Problem with looping', isTgmcmd)
        s.close()
        return
    msgAction('EXITING SHUTDOWN CODE', isTgmcmd)
    s.close()
    sleepTime(30,isTgmcmd)
    #value = subprocess.call('apachectl -k graceful-stop', shell =True)
    value=0
    if value==0:
        msgAction("SHUTDOWN SUCCESS", isTgmcmd)

def startApache():
    #value = subprocess.call('systemctl start apache2', shell =True)
    value=0
    if value==0:
       return msgAction("START SUCCESS", False)
    msgAction("START FAILED", False)


def mainOn(command, isTgmcmd):
    s = startSocket(isTgmcmd)
    s.sendall(command)
    loop_success = fetchdata_loop(s, isTgmcmd)
    if not loop_success:
        msgAction('Problem with looping', isTgmcmd)
        s.close()
        return
    sleepTime(5, isTgmcmd)
    msgAction('EXITING MAINTAINANCE_ON CODE', isTgmcmd)
    s.close()    

def mainOff(command, isTgmcmd):
    s = startSocket(isTgmcmd)
    s.sendall(command)
    loop_success = fetchdata_loop(s, isTgmcmd)
    if not loop_success:
        msgAction('Problem with looping', isTgmcmd)
        s.close()
        return
    sleepTime(5, isTgmcmd)
    msgAction('EXITING MAINTAINANCE_OFF CODE', isTgmcmd)
    s.close()    

def backup(command, isTgmcmd):
    Time = datetime.time(datetime.fromtimestamp(datetime.timestamp(datetime.now())+60*30)).strftime("%H:%M:%S")
    mainOn(bytes(f'30_{Time}','utf-8'),True)
    sleepTime(30, isTgmcmd)
    # INITIATE BACKUP
    s = startSocket(isTgmcmd)
    s.sendall(command)
    s.close()
    
    

def killport(command, isTgmcmd):    
    s = startSocket(isTgmcmd)
    s.sendall(command)
    time.sleep(3)
    data = s.recv(1024)
    if data:
        msgAction(data.decode('utf-8'), isTgmcmd)
        msgAction('KILLPORT COMMAND SEND. USE STATUS TO CHECK OPEN PORT', isTgmcmd)
    else:
        msgAction('Oops !! IT SEEMS THE PORT COULD"NT BE CLOSED. TRY AGAIN OR CHECK STATUS.', isTgmcmd)
    s.close()

def status(command, isTgmcmd):
    s = startSocket(isTgmcmd)
    s.sendall(command)
    time.sleep(3)
    data = s.recv(1024)
    if data:
        msgAction(data.decode('utf-8'), isTgmcmd)
        msgAction('STATUS AVAILABE. PORT OPEN.', isTgmcmd)
    else:
        msgAction('STATUS NOT AVAILABLE. MOST PROBABLY PORT IS CLOSED.', isTgmcmd)
    s.close()


def commandManager(command=False):
    try:
        isTgmcmd = False
        if not command:
            print('CLIENT STARTED')
            command = input(instructions).upper().split('_')
        else:
            command = command.upper().split('_')
            isTgmcmd = True
        msgAction('_'.join(command),isTgmcmd)     
        Time = command[-1] if len(command)>1 else False
        command  = command[0]

        if command not in commandList:
            msgAction(f'Command "{command}" not found. Please check the command list.',isTgmcmd)
            return

        if command == "SHUTDOWN":
            if Time:
                code = 10
                shutdown(bytes(f'{code}_{Time}','utf-8'), isTgmcmd)
            else:
                code = 20
                shutdown(bytes(f'{code}','utf-8'), isTgmcmd)

        elif command == "MAIN-ON":
            if Time:
                code = 30
                mainOn(bytes(f'{code}_{Time}','utf-8'), isTgmcmd)
            else:
                code = 40
                mainOn(bytes(f'{code}','utf-8'), isTgmcmd)

        elif command == 'MAIN-OFF':
            mainOff(bytes('50','utf-8'), isTgmcmd)

        elif command == 'BACKUP':
            backup(bytes('60', 'utf-8'), isTgmcmd)

        elif command  == 'KILLPORT':
            killport(bytes('100', 'utf-8'), isTgmcmd)

        elif command  == 'STATUS':
            status(bytes('80', 'utf-8'), isTgmcmd)

        elif command  == 'START':
            startApache()
            
    except:
        deb = getDebugData()
        with open('logs/maintenance/error.log','a+') as f:
            f.write(deb)
        msgAction(deb, True)
        

threading.Thread(target = startServer, daemon=True).start()
while True:
    time.sleep(1)
    try:clear()
    except:pass
    commandManager()

        
