from config_tpl import config
from moodle.urllist import urlList
from moodle import utils
from moodle.utils import moduleCode
import moodle.SQLclasses
from sharedDB_tpl import dbmoodle as db
import moodle.fetchAPI as fetchAPI
from debug.serverlog import consoleLog, modifyExp
from debug.detector import  exploitRedirect, exploitLog

import requests
import sys
import time
import math
import threading
from random import randint
import re

loginError = {'response':'error', 'msg':'Invalid Username/Password', 'code':11}, 401

def insertGroupToDB(session, loginid, profileID):
    try:
        groupdata = str(fetchAPI.getGroupData(session, profileID))
        newUser = moodle.SQLclasses.group(loginid, profileID, groupdata, True)
        db.session.add(newUser)
        db.session.commit()
    except:
        print_exc_plus(moduleCode, True)
    
def getCookies(session):
    cookieList = []
    for cookie in session.cookies:
        cookieList.append((cookie.name, cookie.value))
    return cookieList


def newUserLogin(loginid, password, userDatabaseDetails):
    session = requests.session()
    session.trust_env = False
    userAgent = getUserAgent()
    updateDB = False
    session.headers.update({'User-Agent': userAgent})

    error, session = fetchLogin(session, loginid, password)
    if error : return session
    hashpassword = utils.data2hash(loginid, password)
    if userDatabaseDetails:
        updateDB = True
    
    # get Moodle Profile ID
    if not updateDB:
        dashboard_data =  fetchDashboard(session, 5000)
        session, dashboard_html = dashboard_data
        sessionKey = re.findall('\"sesskey\":\"(.*?)\"', dashboard_html[800:1000])[0]
        profileID = int(re.findall('data-userid=\"(.*?)\"',  dashboard_html[18200:18400])[0])

    # add user to database
    
    cookieList = getCookies(session)
    if updateDB:
        userDatabaseDetails.passwrd = hashpassword
        userDatabaseDetails.cookies = str(cookieList)
        userDatabaseDetails.time = math.trunc(time.time())
        db.session.commit()

    else: 
        newUser = moodle.SQLclasses.users(loginid, hashpassword, profileID, str(cookieList), math.trunc(time.time()))
        db.session.add(newUser)
        db.session.commit()
        # background
        #threading.Thread(target=insertGroupToDB,args=(session, loginid, profileID,)).start()
    
    return {'response':'OK', 'msg':f'{"Old User:" if updateDB else "New User:"} Login Success !!!'}

def fetchLogin(session, loginid, password, count=0):
    # if count==1: return {'status':False}
    loginUrl = urlList['LOGIN']
    login_page = session.get(loginUrl, verify=False, allow_redirects = False).text
    token = re.search('logintoken\" value=\"(.*?)">',login_page)
    if token:
        token  = token.group(1)
    else:
        modifyExp()
        raise 'Token not found'
    
    keys={'username':loginid, 'password': password, 'logintoken':token, 'anchor':''}
    login = session.post(loginUrl, data = keys, verify = False, allow_redirects = False)
    if login.text.find('testsession') != -1: 
        return 0, session
    return 1, loginError

def fetchDashboard(session, maxlimit):
    dashboard = session.get(urlList['DASHBOARD'], verify = False, allow_redirects = False, stream = True)
    dashboard_html = utils.chunkDownloader(dashboard, maxlimit)
    if dashboard_html.find('login/index.php') != -1:
        return False
    return session, dashboard_html


def oldUserLogin(loginid, password, queryResult, userAgent):
    cookieTime, dbPassword, cookies, profileID = queryResult.time, queryResult.passwrd, eval(queryResult.cookies), queryResult.moodleID
    hashpassword = utils.data2hash(loginid, password)

    if hashpassword != dbPassword:
        exploitLog(sys._getframe(), moduleCode)
        return exploitRedirect(), 418

    session = requests.session()
    session.trust_env = False

    for cookie in cookies:
        session.cookies.set(cookie[0], cookie[1], domain = urlList['DOMAIN'])
    session.headers.update({'User-Agent':userAgent})
    cookieUpdate =  False
    Time = math.trunc(time.time())

    reLogin = True
    if Time - queryResult.time < config['MOODLE_TIMEOUT']:
        dashboard_data = fetchDashboard(session, 600)
        reLogin = not dashboard_data

    if reLogin:
        session.cookies.clear()
        error, session = fetchLogin(session, loginid, password)
        if error : return session
        dashboard_data =  fetchDashboard(session, 600)
        cookieUpdate = True
    session, dashboard_html = dashboard_data
    sessionKey = re.findall('\"sesskey\":\"(.*?)\"', dashboard_html[800:1000])[0]

    if cookieUpdate:
        cookieList = getCookies(session)
        queryResult.cookies = str(cookieList)
        queryResult.time = math.trunc(time.time())
        db.session.commit()

    return getMoodleBulkData(session, sessionKey)

def getMoodleBulkData(session, sessionKey):
    return {'assign':fetchAPI.getAssignmentData(session, sessionKey),'response':'OK'}


##def getMoodleBulkData(session, sessionKey):
##    thread1 = utils.ThreadWithReturn(target = fetchAPI.getAssignmentData, args=(session, sessionKey, ))
##    thread1.start()
##    AssignmentData = thread1.join()
##    return {'assign':AssignmentData,'response':'OK'}
    
def getUserAgent():
    userAgentList = config['USER_AGENTS']
    return userAgentList[randint(0,len(userAgentList)-1)]

def loginHandler(loginid, password, queryResult):
    if not queryResult:
        # attempt to exploit API// Url only to be used for existing user
        exploitLog(sys._getframe(), moduleCode)
        return exploitRedirect(), 418
    userAgent = getUserAgent()
    return oldUserLogin(loginid, password, queryResult, userAgent)
