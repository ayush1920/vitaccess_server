import socket
import telegram.bot as tgbot
from debug.serverlog import consoleLog
from maintenance import socketServer as ssr
import requests as rq

HOST = '127.0.0.1'
PORT = 42069

failmessage = '''Internal Command error. No condition available in file internalHandler.py file.
Choose commands from this list:-
/kill
/startport
/shutdown HH:MM
/mainon HH:MM
/mainoff
/backup
/status
/moodleE
/moodleD
/vtopE
/vtopD
/maintenanceE
/telegramE
/counter
/resetCounter
/lastBackupCheck
'''

checked = {'time':'0'}

def updateCheck(Time):
    checked['time'] = Time

def sendCommand(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(bytes(command, 'utf-8'))
    s.close()
    
def processCommand(command):
    hasParam = False
    split = command.split(' ')

    if len(split)>1:
        hasParam = True
        cmd, param = split[0], split[1]
    else:
        cmd = split[0]
    if cmd == '/kill':
        sendCommand('KILLPORT')
    elif cmd == '/startport':
        ssr.start()
        msg = 'START COMMAND SENT. CHECK STATUS BY USING /status command'
        url = f"https://api.telegram.org/bot1152939742:<telegram_api_key>/sendMessage?chat_id=<chat_id>&text={msg}"
        res = rq.get(url)
        
    elif cmd =='/shutdown':
        if hasParam: sendCommand(f'SHUTDOWN_{param}')
        else:
            sendCommand('SHUTDOWN')

    elif cmd =='/mainon':
        if hasParam:sendCommand(f'MAIN-ON_{param}')
        else: sendCommand('MAIN-ON')

    elif cmd =='/mainoff':
        sendCommand('MAIN-OFF')

    elif cmd == '/backup':
        sendCommand('BACKUP')

    elif cmd == '/status':
        sendCommand('STATUS')
        
    elif cmd=='/lastBackupCheck':
        tgbot.bot.send_message(str(checked['time']))

    elif cmd =='/resetCounter':
        tgbot.bot.resetCounter()

    elif cmd == '/counter':
        tgbot.bot.send_message(str(tgbot.bot.counter))   

    elif cmd == '/moodleE':
        tgbot.bot.uploadFile('logs/moodle/exploit.log')

    elif cmd =='/moodleD':
        tgbot.bot.uploadFile('logs/moodle/debug.log')

    elif cmd == '/vtopE':
        tgbot.bot.uploadFile('logs/vtop/exploit.log')

    elif cmd =='/vtopD':
        tgbot.bot.uploadFile('logs/vtop/debug.log')

    elif cmd =='/maintenanceE':
        tgbot.bot.uploadFile('logs/maintenance/error.log')

    elif cmd =='/telegramE':
        tgbot.bot.uploadFile('logs/telegram/telegramError.log')
        
    else:
        tgbot.bot.send_message(failmessage)            
    
