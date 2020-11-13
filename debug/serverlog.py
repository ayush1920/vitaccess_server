import sys
import click._compat

from debug.utils import checknCreate
import traceback
import logging
import logging.handlers as handlers
from datetime import datetime
import debug.multiprocessing_logging as multiprocessing_logging
import glbvar
import telegram.bot as tgbot

def consoleLog(text):
    click.secho(str(text), fg='green')

moluleDict = {
    1:'VTOP',
    2:'MOODLE',
    3:'TELEGRAM'
    }

def initiate_logger(logger_name, logger_location):
    logg = logging.getLogger(logger_name)
    logg.setLevel(logging.DEBUG)
    checknCreate(logger_location)
    file_handler = handlers.TimedRotatingFileHandler(logger_location,when='midnight')
    logg.addHandler(file_handler)
    multiprocessing_logging.install_mp_handler(logg)
    return logg

vtop_log = initiate_logger("VTOP_LOGGER", 'logs/vtop/debug.log')
moodle_log = initiate_logger("MOODLE_LOGGER", 'logs/moodle/debug.log')
checknCreate('logs/maintenance/error.log')
displayLog = glbvar.logDisplay.display

responseData = {1:({'response':'error', 'msg':'Catched Server Error', 'code':21},503),2:False}

def modifyExp(response = {'response':'error', 'msg':'Catched Server Error', 'code':21}, code = 503):
    responseData[1] = (response, code)
    responseData[2] = True

def appendData(initial, data):
    return initial + data +'\n'
    



def print_exc_plus(mod = 1, force = False, exceptionData = False):
    useResponse = False
    exc = sys.exc_info()
    # use force for logging threaded process error
    resp = ''
    if force:
        if exceptionData: exc = exceptionData
    else:
        if responseData[2]:
            useResponse = True
            resp = responseData[1]
            responseData[2] = False
    
    deb = getDebugData(exc, useResponse, resp)
    
    if mod == 1:
        vtop_log.debug(deb)
    elif mod == 2:
        moodle_log.debug(deb)
    elif mod==3:
        with open('logs/maintenance/error.log', 'a+') as f:
            f.write(deb)
    # Remove this line in production
    if displayLog: consoleLog(deb)
    try:
        tgbot.bot.uploadLog(f'Error in module: {moluleDict[mod]}',deb)
    except:
        print('Telegram BOT Error in serverlog.py')
    return resp


def getDebugData(exc, useResponse, resp):
    deb = '-'*20
    deb = appendData(deb, datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'-'*20)
    deb = appendData(deb, 'Res Code:'+str(resp[-1] if useResponse else 500))
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
    
def independentDebug():
    def appendData(initial, data):
        return initial + data +'\n'

    exc = sys.exc_info()
    deb = '-'*20
    deb = appendData(deb, datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'-'*20)
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
