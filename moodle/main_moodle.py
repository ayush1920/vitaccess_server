from flask import Flask, Blueprint, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import time
import sys

from moodle import login
from moodle.utils import moduleCode
from maintenance import socketServer as ssr
import moodle.SQLclasses as SQLclasses
from debug.serverlog import consoleLog, modifyExp, print_exc_plus
from debug.detector import  exploitRedirect, exploitLog
moodleBlueprint = Blueprint('moodleBlueprint', __name__, static_folder='static', template_folder='templates')


def verifyLogin(cred):
    try:
        username = cred['username'].upper()
        password = cred['password']
        userDatabaseDetails = SQLclasses.users.query.filter_by(regno = username).first()
        return username, password, userDatabaseDetails
    except:
        exploitLog(sys._getframe(), moduleCode)
        modifyExp(exploitRedirect(), 418)
        raise Exception('Error in getting username/password')


def catchException(error = {'response':'error', 'msg':'Internal Server Error', 'code':20}, code = 500):
    resp = print_exc_plus(moduleCode)
    if resp:
        return resp
    return error, code


@moodleBlueprint.route('/bulk', methods = ["POST"])
def fetch_Bulkdata():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.loginHandler(username, password, userDatabaseDetails)
    except:
        return catchException()

@moodleBlueprint.route('/register', methods = ["POST"])
def process_Register():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.newUserLogin(username, password, userDatabaseDetails)
    except:
        return catchException()
