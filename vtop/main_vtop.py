from flask import Flask, Blueprint, render_template, request, jsonify, Response, redirect
from flask_sqlalchemy import SQLAlchemy

import time
import requests
import sys

import vtop.SQLclasses as SQLclasses
from maintenance import socketServer as ssr
from vtop import login
from vtop import fetchAPI
from debug.serverlog import print_exc_plus, modifyExp
from debug.detector import exploitRedirect, exploitLog

vtopBlueprint = Blueprint('vtopBlueprint', __name__, static_folder='static', template_folder='templates')

# -------- functions ------------------

def verifyLogin(cred):
    try:
        username = cred['username'].upper()
        password = cred['password']
        userDatabaseDetails = SQLclasses.users.query.filter_by(regno = username).first()
        return username, password, userDatabaseDetails
    except:
        exploitLog(sys._getframe())
        modifyExp(exploitRedirect(), 418)
        raise Exception('Error in getting username/password')

def catchException(error = {'response':'error', 'msg':'Internal Server Error', 'code':20}, code = 500):
    resp = print_exc_plus()
    if resp:
        return resp
    return error, code

# --------- route List -----------------

@vtopBlueprint.route('/test', methods = ["GET"])
def test():
    import vtop.test3
    vtop.test3startTest()


@vtopBlueprint.route('/register', methods = ["POST"])
def process_Register():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.newUserLogin(username, password, userDatabaseDetails)
    except:
        return catchException()
        


@vtopBlueprint.route('/bulk', methods = ["POST"])
def fetch_Bulkdata():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.loginHandler(username, password, userDatabaseDetails)
    except:
        return catchException()

@vtopBlueprint.route('/timetable', methods = ["POST"])
def fetch_TimeTable():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.otherHandler('timetable', username, password, userDatabaseDetails)
    except:
        return catchException()


@vtopBlueprint.route('/gradelist', methods = ["POST"])
def fetch_GradeList():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.otherHandler('gradelist', username, password, userDatabaseDetails)
    except:
        return catchException()


@vtopBlueprint.route('/gradecalc', methods = ["POST"])
def fetch_GradeCalc():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.otherHandler('gradecalc', username, password, userDatabaseDetails)
    except:
        return catchException()



@vtopBlueprint.route('/attendance', methods = ["POST"])
def fetch_Attendance():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.otherHandler('attendance', username, password, userDatabaseDetails)
    except:
        return catchException()


@vtopBlueprint.route('/marks', methods = ["POST"])
def fetch_Marks():
    try:
        if ssr.server.res:return ssr.server.resp
        cred = request.get_json(force=True, silent = True)
        username, password, userDatabaseDetails  = verifyLogin(cred)
        return login.otherHandler('marks', username, password, userDatabaseDetails)
    except:
        return catchException()


@vtopBlueprint.route("/getDate", methods = ['GET','POST'])
def curdate():
    from datetime import datetime
    import pytz
    monthlist={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec" }
    date = str(datetime.now(pytz.timezone('Asia/Kolkata'))).split(" ")[0].split("-")[::-1]
    date[1]=monthlist[int(date[1])]
    return "-".join(str(x) for x in date)
