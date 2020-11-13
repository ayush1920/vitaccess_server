from flask import Flask, Blueprint, render_template, request, redirect
import sys
from debug.serverlog import consoleLog, print_exc_plus
import telegram.bot as tgbot
import telegram.internalHandler as handler

tgmBlueprint = Blueprint('tgmBlueprint', __name__, static_folder='static', template_folder='templates')

bot = tgbot.bot

@tgmBlueprint.route('/cmnd',methods = ['POST'])
def receiveCommand():
    try:
        js = request.get_json(force=True, silent = True)
        if js['message'].get('entities',None) and js['message']['chat']['id']== <user_id>:
            handler.processCommand(js['message']['text'])
        return 'Command Success'
    except:
        print_exc_plus(mod = 3, force = True, exceptionData = sys.exc_info())
        return 'command success', 200
