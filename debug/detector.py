# EXPLOIT detector file
import os
from datetime import datetime
from debug.mltwrite import mltFileWriter as mltFileWriter
from debug.utils import checknCreate
import telegram.bot as  tgbot

def createWriter(path):
    checknCreate(path)
    return mltFileWriter(path)
    

vtopLog = createWriter('logs/vtop/exploit.log')
moodleLog = createWriter('logs/moodle/exploit.log')
modeDict = {
    1: 'VTOP',
    2: 'MOODLE'
    }

def exploitRedirect():
    return {'response':'error', 'msg':'I\'m a teapot. Don\'t expect me to (brew coffee) do things I am not programmed for !!!\nFind more on: https://vitaccess.tech/418', 'code':31}

# -- not a safe method to log files. Use for low traffic methods

def exploitLog(frame, mode = 1):
    raiseFun, varlist = str(frame.f_code.co_name), frame.f_locals
##    pops 'password' variable for security resons.
##    varlist.pop('password', None)
##    newline = '\n\t'
    data = '%s\nDate: %s Function:%s\n%s\n\t%s\n'%('-'*20, datetime.now(), raiseFun, '-'*20, '\n\t'.join([f"{i}:{varlist[i]}" for i in varlist]))
    if mode == 1:
        vtopLog.writeData(data)
    elif mode == 2:
        moodleLog.writeData(data)
    tgbot.bot.uploadLog(f'Exploit {modeDict[mode]}.log',data)

## Use this methood flush log before shutdown
def flushLogs():
    vtopLog.flush()
    moodleLog.flush()
