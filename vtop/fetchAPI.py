from vtop.urllist import urlList, serverUrl
from debug.serverlog import consoleLog
from vtop.formatDate import getDate
import vtop.parse as parse

def parseData(data,method):
    if 'Anthoniraj' in data[:100]:
        return False
    return method(data)
    

def Attendance(session, loginid):
    attendance_page = "http://vtopcc.vit.ac.in:8080/vtop/processViewStudentAttendance"
    keys={'semesterSubId':"CH2020211",'authorizedID': loginid,'x':getDate()}
    attendanceHtml = session.post(attendance_page, data=keys,verify=False).text
    return parseData(attendanceHtml, parse.attendanceParse)
    
def Marks(session, loginid):
    marks_page = "http://vtopcc.vit.ac.in:8080/vtop/examinations/doStudentMarkView"
    marksHtml = session.post(marks_page,files={'authorizedID': (None, loginid), 'semesterSubId': (None, 'CH2020211')},verify=False).text
    return parseData(marksHtml, parse.marksParse)

def TimeTable(session, loginid):
    routine_page = 'http://vtopcc.vit.ac.in:8080/vtop/processViewTimeTable'
    keys={'semesterSubId':"CH2020211",'authorizedID': loginid,'x':getDate()}
    routineHtml = session.post(routine_page, data=keys, verify=False).text
    return parseData(routineHtml, parse.routineParse)

def GradeList(session, loginid):
    grade_page = 'http://vtopcc.vit.ac.in:8080/vtop/examinations/examGradeView/StudentGradeHistory'
    keys = {'verifyMenu':'true', 'winImage':'undefined', 'authorizedID':loginid,'nocache':'@(new Date().getTime())'}
    GradelistHtml = session.post(grade_page, data = keys, verify=False).text
    return parseData(GradelistHtml, parse.gradelistParse)

def GradeCalc(session, loginid):
    routine_page = 'http://vtopcc.vit.ac.in:8080/vtop/processViewTimeTable'
    keys={'semesterSubId':"CH2020211",'authorizedID': loginid,'x':getDate()}
    GradeCalcHtml = session.post(routine_page, data=keys, verify=False).text
    return parseData(GradeCalcHtml, parse.gradecalcParse)

def Name(session, loginid):
    data = {'verifyMenu':'true', 'winImage':'undefined', 'authorizedID':loginid,'nocache':'@(new Date().getTime())'}
    nameHtml = session.post('http://vtopcc.vit.ac.in:8080/vtop/studentsRecord/StudentProfileAllView', data = data).text
    return parseData(nameHtml, parse.nameParse) 
    
