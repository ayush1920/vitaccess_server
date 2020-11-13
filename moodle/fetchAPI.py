import datetime
import requests
from moodle.urllist import urlList, serverUrl
from moodle.urllist import serverUrl
from debug.serverlog import consoleLog, modifyExp
import re
import json

def getAssignmentData(session, sessionKey):
    try:
        timestampfrom = int(datetime.datetime.timestamp( datetime.datetime.combine((datetime.datetime.now() - datetime.timedelta(days = 7)).date(), datetime.datetime.min.time())))
        timestampto = int(datetime.datetime.timestamp( datetime.datetime.combine((datetime.datetime.now() + datetime.timedelta(days = 14)).date(), datetime.datetime.min.time())))
        jsondata = [{"index":0,"methodname":"core_calendar_get_action_events_by_timesort","args":{"limitnum":11,"timesortfrom":timestampfrom,'timesortto':timestampto}}]
        jsonresponse = session.post(f'{serverUrl}/lib/ajax/service.php?sesskey={sessionKey}&info=core_calendar_get_action_events_by_timesort',json = jsondata, verify = False)
        jsonObj = json.loads(jsonresponse.text)[0]
        if jsonObj['error']:
            raise 'JSON response error'
        assignList = jsonObj['data']['events']
        data = []
        for i in assignList:
            data.append([i['id'], i['name'], i['course']['fullname'], i['timesort'],i['component']])
        return {'assignmentData':data,'response':'OK'}
    except:
        modifyExp()
        raise 'function getAssignmentData'


def getGroupData(session, profileID):
    userprofileURL = f'{urlList["PROFILE"]}?id={profileID}'
    userprofile = session.get(userprofileURL, verify = False)
    courseList = re.findall(f'/user/view.php\?id={profileID}&amp;course=(.*?)\">(.*?)</a>', userprofile.text, re.DOTALL)

    parsedCourse = []
    # ! IMPORTANT -> Problem might occur if course code is not availabe or format changes.
    # ! Test the code and implement try-catch before deployment.
    
    for course in courseList:
        courseId = int(course[0])
        courseName = course[1].split('(')[0]
        if '(' and ')' not in course[1]:
            continue
        courseCode = course[1].split('(')[1][:-1]
        parsedCourse.append((courseId, courseName, courseCode))
    # parsedCourse = list(zip(map(lambda x:int(x[0]),courseList),map(lambda x:x[1].split('(')[0], courseList), map(lambda x:x[1].split('(')[1][:-1], courseList)))
        
    course_group_name = []
    for data in parsedCourse:
        courseid, courseName, courseCode = data
        course_url = f'https://lms.vit.ac.in/user/view.php?id={profileID}&course={courseid}'
        course_data = session.get(course_url , verify = False)
        groupid_name = re.findall(f'https://lms.vit.ac.in/user/index.php\?id={courseid}&amp;group=(.*?)\">(.*?)</a>', course_data.text, re.DOTALL)

        # filter lab classes
        groupid_name = [group for group in groupid_name  if group[1].split('(')[1].count('L')<2]
        # # new solt error check
        # if len(groupid_name)>1 and groupid_name[0][1].split('(')[0]!=groupid_name[1][1].split('(')[0]:
        #     # generate error
        #     consoleLog('error')
        #     pass
        groupid, groupname = int(groupid_name[0][0]), groupid_name[0][1].split('(')[0]
        course_group_name.append([courseid, groupid, courseCode, courseName, groupname])
    return course_group_name
