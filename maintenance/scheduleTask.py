import time
import datetime
import threading
import telegram.bot as tgbot
import telegram.internalHandler as handler
from debug.serverlog import independentDebug, consoleLog
import sys

trig = {'count':0}

def schedule():
    time.sleep(10)
    while True:
        try:
            handler.updateCheck(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if datetime.datetime.now().hour == 21:
                if trig['count'] == 0:
                    # start periodic process
                    trig['count']=1
                    handler.processCommand('/backup')
                    tgbot.bot.resetCounter()
            else:
                trig['count'] = 0
        except:
            deb = independentDebug()
            tgbot.bot.uploadLog('secheduleTaskError',deb)
            with open('logs/maintenance/error.log','a+') as f:
                f.write(deb)
            consoleLog(deb)
        time.sleep(30*60)

def start():
    threading.Thread(target = schedule, daemon = True).start()
