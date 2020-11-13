from flask import Flask,render_template,request, jsonify, url_for, make_response, redirect
import urllib3
import sqlalchemy
import validateFolder
import os
os.chdir(os.path.dirname(__file__))

import glbvar
glbvar.logDisplay.enable() # enable logDisplay


from flask_sqlalchemy import SQLAlchemy
from debug.serverlog import consoleLog
from config_tpl import config
from moodle.main_moodle import moodleBlueprint
from vtop.main_vtop import vtopBlueprint
from telegram.main_tgm import tgmBlueprint
from sharedDB_tpl import dbvtop, dbmoodle
from utils import initializeDB, forceTCP4
from maintenance import socketServer as ssr
from maintenance import scheduleTask



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # supress SSL warnings
forceTCP4() # force requests for TCP/IP4

def InitializeOneTime(requirePass = True, trigger=1, pas =''):
    try:
        if requirePass and pas !='anmrst99':
            return "Internal ERROR"
        if trigger ==1:
            initializeDB()
        elif trigger ==2 :
            ssr.start()
        if requirePass:
            return 'SUCCESS'
    except:
        if requirePass:
            return "Internal ERROR"

app = Flask(__name__)
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config['VTOP_DATABASE']
app.config['SQLALCHEMY_BINDS']= {'moodle': config['MOODLE_DATABASE']}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

dbvtop.app = app
dbvtop.init_app(app)
dbmoodle.app = app
dbmoodle.init_app(app)
app.register_blueprint(moodleBlueprint, url_prefix = '/api/moodle')
app.register_blueprint(vtopBlueprint, url_prefix = '/api/vtop')
app.register_blueprint(tgmBlueprint, url_prefix = '/tgm')

InitializeOneTime(False,1)
InitializeOneTime(False,2)
scheduleTask.start()

# ---------------- ADMIN Functions ---------------------

@app.route('/intiDB', methods = ["POST"])
def adminCreateDatabase():
    try:
        pas = request.args.get('pass')
    except:
        return 'INTERNAL ERROR'
    return InitializeOneTime(True,1,pas)


@app.route('/startSocket', methods = ["POST"])
def startSocket():
    try:
        pas = request.args.get('pass')
    except:
        return 'INTERNAL ERROR'
    return InitializeOneTime(True,2,pas)


##@app.before_first_request
##def autoInit():
##    adminCreateDatabase(False)
##    startSocket(False)
#--------------------- END SECTION ------------------------    









# --------------------- trash code -------------------------
@app.route('/418', methods = ["GET"])
def mugiRedirect():
    return redirect("https://i.ibb.co/7nP2pH6/mugi-kon.png", code=302)
# --------------------- END SECTION -------------------------    

if __name__ =='__main__':
    app.run(debug=True, use_reloader=False)

    
