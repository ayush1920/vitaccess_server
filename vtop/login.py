from config_tpl import config
from vtop.urllist import urlList
from vtop import utils
import vtop.SQLclasses
from sharedDB_tpl import dbvtop as db
import vtop.fetchAPI as fetchAPI
from debug.serverlog import consoleLog, modifyExp, print_exc_plus
from debug.detector import  exploitRedirect, exploitLog
import vtop.captcha as captcha  
import vtop.marksupdater

import requests
import time
import math
import threading
from random import randint
import json
import sys

loginError = {'response':'error', 'msg':'Invalid Username/Password', 'code':10}, 401    

# Requery because session commit won't happen on thread.
def marksUpdate(loginid ,newmarks):
    try:
        userMarksDetails = vtop.SQLclasses.marks.query.filter_by(regno = loginid).first()
        formatOld = eval(userMarksDetails.marks)
        cntOld, cntNew = 0,0
        for i in formatOld.values():
            cntOld += i
        for i in newmarks['marks']:
            cntNew += len(i)
        if cntOld == cntNew:
            return False
        formatNew =  {i[0]:[[j[0],float(j[4])] for j in i[1]] for i in zip(map(lambda x:int(x[0]),newmarks['subdata']),newmarks['marks'])}

        #formatOld = {i[0]:i[1] for i in zip(map(lambda x:int(x[0]),oldmarks['subdata']),oldmarks['marks'])}
        newKeys = formatNew.keys()
        newData = {}
        for i in newKeys:
            subjectSl = formatOld.get(i,0)
            notAvail = {item[0]:item[1] for item in formatNew[i] if item[0]> subjectSl}
            if notAvail:
                newData[i]  = notAvail
        thrd = utils.ThreadWithReturn(target = vtop.marksupdater.avgClass.update,args= (newData,))
        thrd.start()
        res, exceptionData = thrd.join()
        consoleLog(formatNew)
        if res:
            # commit changes
            userdataQuery = vtop.SQLclasses.users.query.filter_by(regno = loginid).first()
            userdataQuery.marksTime = math.trunc(time.time())
            saveData = {key:len(formatNew[key]) for key in formatNew.keys()}
            userMarksDetails.marks = str(saveData)
            consoleLog(saveData)
            db.session.commit()
        else:
            print_exc_plus(mod =1, force = True, exceptionData = exceptionData)
    except:
        print_exc_plus()

def AvgMarks(marks):
    try:
        queryDict = {i[0]:[int(x[0]) for x in i[1]] for i in zip(map(lambda x:int(x[0]),marks['subdata']),marks['marks'])}
        return vtop.marksupdater.avgClass.getAvg(queryDict)
    except:
        modifyExp()
        raise Exception('error in fetchMarks')
         
def setSession(loginid, password, dbPassword, cookies, userAgent):
    isExploit = False
    hashpassword = utils.data2hash(loginid, password)
    if hashpassword != dbPassword:
        isExploit = True
        
    session = requests.session()
    session.trust_env = False
    for cookie in cookies:
        session.cookies.set(cookie[0],cookie[1])
    session.headers.update({'User-Agent':userAgent})
    return session, isExploit


def fetchSection(loginid, password, queryResult, userAgent, fetchFunction):
    cookieTime, dbPassword, cookies  = queryResult.time, queryResult.passwrd, eval(queryResult.cookies)
    session, isExploit = setSession(loginid, password, dbPassword, cookies, userAgent)
    if isExploit:
        exploitLog(sys._getframe())
        return exploitRedirect(), 418

    reLogin = True
    updateCookie = False
    Time = math.trunc(time.time())
    if Time - cookieTime < 900:
        data = fetchFunction(session, loginid)
        reLogin = not data
        
    if reLogin:
        session.cookies.clear()
        error, session = fetchLogin(session, loginid, password)
        if error: return session
        data = fetchFunction(session, loginid)
        updateCookie = True
    if fetchFunction.__name__ == 'Marks':
        avg  = AvgMarks(data['marksdata'])
        data['marksdata']['AvgData'] = avg

    if updateCookie:
        queryResult.cookies = str(getCookies(session))

    queryResult.time  = Time
    db.session.commit()
    return data
    
    

def getName(session, loginid):
    return fetchAPI.Name(session, loginid)
       
def getCookies(session):
    cookieList = []
    for cookie in session.cookies:
        cookieList.append((cookie.name, cookie.value))
    return cookieList


def getUserAgent():
    userAgentList = config['USER_AGENTS']
    return userAgentList[randint(0,len(userAgentList)-1)]


def newUserLogin(loginid, password, userDatabaseDetails):
    session = requests.session()
    session.trust_env = False
    userAgent = getUserAgent()
    updateDB = False
    session.headers.update({'User-Agent': userAgent})
    error, session = fetchLogin(session, loginid, password)
    if error: return loginError
    hashpassword = utils.data2hash(loginid, password)
    if userDatabaseDetails:
        updateDB = True
    
    # getName
    if not updateDB: name = getName(session, loginid)
        
    # add user to database
    Time =  math.trunc(time.time())
    cookieList = getCookies(session)
    if updateDB:
        userDatabaseDetails.passwrd = hashpassword
        userDatabaseDetails.cookies = str(cookieList)
        userDatabaseDetails.time = Time
        userDatabaseDetails.marksTime = 0
        db.session.commit()

    else: 
        newUser = vtop.SQLclasses.users(loginid, hashpassword, str(cookieList), Time, name, 0)
        newMarks = vtop.SQLclasses.marks(loginid, "{}")
        db.session.add(newUser)
        db.session.add(newMarks)
        db.session.commit()
    
    return {'response':'OK', 'msg':f'{"Old User:" if updateDB else "New User:"} Login Success !!!'}

def fetchLogin(session, loginid, password):
    
    vtop_page = "http://vtopcc.vit.ac.in:8080/vtop/"
    login_page = "http://vtopcc.vit.ac.in:8080/vtop/vtopLogin"
    doLogin_page = "http://vtopcc.vit.ac.in:8080/vtop/doLogin"
    
    login = session.get(vtop_page, verify = False, stream = True)
    utils.chunkDownloader(login, 10)
    pageSource = session.get(login_page, verify = False).text
    cap,msg =  captcha.break_captcha(pageSource)
    if not cap:
        if msg == 'VIT_ERROR':
            modifyExp(response ={'response':'error', 'msg':'VTOP server is not responding', 'code':22},code = 503)
        else:
            modifyExp()
        raise Exception('captcha failed') 
    keys={'uname': loginid,'passwd': password,'captchaCheck':cap}
    dologin =  session.post(doLogin_page,data=keys,verify=False, stream = True)
    chunkdata  = utils.chunkDownloader(dologin, 200)

    if 'container-fluid' in chunkdata[150:]:
        return 0, session
    return 1,loginError

def oldUserLogin(loginid, password, queryResult, userAgent):
    cookieTime, dbPassword, cookies, marksTime = queryResult.time, queryResult.passwrd, eval(queryResult.cookies), queryResult.marksTime
    hashpassword = utils.data2hash(loginid, password)
    if hashpassword != dbPassword:
        exploitLog(sys._getframe())
        return exploitRedirect(), 418

    session = requests.session()
    session.trust_env = False
    
    for cookie in cookies:
        session.cookies.set(cookie[0],cookie[1])
    session.headers.update({'User-Agent':userAgent})
    cookieUpdate =  False
    Time = math.trunc(time.time())
    # test login by fetching attendance, relogin
    reLogin = True
    if Time - queryResult.time < 900:
        attendance_data = fetchAPI.Attendance(session, loginid)
        # fetching attendance failed. User might logged in from another device.
        reLogin = not attendance_data

    if reLogin:
        session.cookies.clear()
        error, session = fetchLogin(session, loginid, password)
        if error: return loginError
        attendance_data = fetchAPI.Attendance(session, loginid)
        cookieUpdate = True

    # fetch marks data
    marks = fetchAPI.Marks(session, loginid)    
    if not marks:
        modifyExp()
        raise Exception('Attendance fetched but not marks')

    avg  = AvgMarks(marks['marksdata'])
    marks['marksdata']['AvgData'] = avg

    if cookieUpdate:
        cookieList = getCookies(session)
        queryResult.cookies = str(cookieList)

    queryResult.time = Time
    db.session.commit()

    if Time - marksTime > 86400:
        threading.Thread(target = marksUpdate, args= (loginid, marks['marksdata'],)).start()
    
    return {'attendance':attendance_data,'marks':marks, 'response':'OK'}


# fetchTimeTable should be used rarely. Log frequency for testing API exploitation.
def fetchTimeTable(loginid, password, queryResult, userAgent):
    return fetchSection(loginid, password,queryResult, userAgent, fetchAPI.TimeTable)
     

# fetchGradeList should be used rarely. Log frequency for testing API exploitation.
def fetchGradeList(loginid, password, queryResult, userAgent):
    return fetchSection(loginid, password,queryResult, userAgent, fetchAPI.GradeList)


# fetchGradeCalc should be used rarely. Log frequency for testing API exploitation.
def fetchGradeCalc(loginid, password, queryResult, userAgent):
    return fetchSection(loginid, password,queryResult, userAgent, fetchAPI.GradeCalc)
    
# ---------- should never be used by client ------------
def fetchAttendance(loginid, password, queryResult, userAgent):
    return fetchSection(loginid, password,queryResult, userAgent, fetchAPI.Attendance)

# ---------- should never be used by client ------------
def fetchMarks(loginid, password, queryResult, userAgent):
    return fetchSection(loginid, password, queryResult, userAgent, fetchAPI.Marks)


def otherHandler(datarequest,loginid, password, queryResult):
    if not queryResult:
        # attempt to exploit API// Url only to be used for existing user
        exploitLog(sys._getframe())
        return exploitRedirect(), 418
    
    userAgent = getUserAgent()
    if datarequest == 'timetable':
        return fetchTimeTable(loginid, password, queryResult, userAgent)
    if datarequest == 'gradelist':
        return fetchGradeList(loginid, password, queryResult, userAgent)
    if datarequest == 'gradecalc':
        return fetchGradeCalc(loginid, password, queryResult, userAgent)
    if datarequest == 'attendance':
        return fetchAttendance(loginid, password, queryResult, userAgent)
    if datarequest == 'marks':
        return fetchMarks(loginid, password, queryResult, userAgent)

def loginHandler(loginid, password, queryResult):
    if not queryResult:
        # attempt to exploit API // Url only to be used for existing user
        exploitLog(sys._getframe())
        return exploitRedirect(), 418

    userAgent = getUserAgent()
    return oldUserLogin(loginid, password, queryResult, userAgent)
