import re
import codecs
import json
from debug.serverlog import modifyExp

def attendanceParse(data):
    try:
        JSONformat ={}
        classno = re.findall("AttendanceDetail\(&#39;(.*?)&#39;", data)
        data = re.findall("style=\"margin: 0px;\">(.*?)</p>",data)
        data = [{'uid':classno[i//9][-5:],'value':[data[i+1],data[i+2],data[i+6],data[i+7],data[i+8]]} for i in range(0, len(data), 9)]
        JSONformat['total'] = len(data)
        JSONformat['values'] = data
        response = "OK"
        if data:
            return {'attendance' : JSONformat, "response" : response}
        raise ValueError('Empty data')
    except:
        modifyExp()
        raise Exception('error in attendanceParse')


def marksParse(s):
    try:
        s=s.replace('\r','').replace('\t','')
        p=s
        JSONformat = {}
        s = re.findall("tableContent-level1\">(.*?)</tr>",s,re.DOTALL)
        l =[]
        m = []
        for i in s:
        #if i[0:28]=='\n<td><output>1</output></td>':
            k =i.replace('></output>','').replace('</output>','$').replace('output','').replace('td','').replace('\n','').replace('/','').replace('<','').replace('>','')[:-1:].split('$')[:7]
            if int(k[0])==1:
                l.append(m)
                m = []
            m.append([int(k[0]), k[1].replace('Digital Assignment','DA').replace('Continous Assessment Test','CAT'),k[2],k[3],k[5],k[6]])
        # if end
        l.append(m)
        del l[0]
        # subject
        cpy=[]
        p = re.findall('<tr class=\"tableContent\" >(.*?)<\/tr>',p,re.DOTALL)
        
        for i in p:
            k = i.replace('\t','').replace('</td>\n','$').replace('<td>','').replace('\n','')[:-1:].split('$')
            cpy.append([k[1][-5:], k[2], k[3], k[6]])
        if cpy and l: 
            JSONformat['subdata'] = cpy
            JSONformat['marks'] = l
            return {'marksdata' : JSONformat, 'response':'OK'}

        raise ValueError('Empty data')
    except:
        modifyExp()
        raise Exception('error in marksParse')

# New  function independent of changes is timing and no. of classes
def routineParse(s):
    def processLab(lb):
        new = []
        time = ''
        old=''
        for ind,i in enumerate(lb):
            if time == '':
                time = i[1]
                old =  i
            else:
                if i[2] == old[2]:
                    time+=i[1]
                else:
                    splt = time.split('-')
                    time = '-'.join([splt[0],splt[-1]])
                    old[1] = time
                    new.append(old)
                    time=i[1]
                    old =  i
        if time!='':
            splt = time.split('-')
            time = '-'.join([splt[0],splt[-1]])
            old[1] = time
            new.append(old)
        return new

    try:
        courseTable = re.search("<table class=\"table\"(.*?)<\/table>",s,re.DOTALL).group(1)
        courseCol  = re.findall('#3c8dbc;vertical-align: middle;text-align: left;\">(.*?)</td>', courseTable)
        lis = []
        emptyCheck = 1 
        for i in courseCol:
            temp = i.split(' - ')
            lis.append([temp[0],temp[1]])
        # lis contains names of subject and subject code as it is in the table // list
        classInfo= re.findall('<p style=\"margin: 0px;\">(.*?)</p>',courseTable)
        r = {lis[i//9][0]+'-'+classInfo[i:i+8][6]: [classInfo[i:i+8][4][-5:], lis[i//9][1]] for i in range(0,len(classInfo),9)}
        # r contains subject code and roomno mapped with classno and subject name // dict
        s = re.search("<table id=\"timeTableStyle\"(.*?)<\/table>",s,re.DOTALL).group(1).replace('\r','').replace('\t','').replace('\n','')
        JSONformat = []
        day =['MON','TUE','WED','THU','FRI','SAT','SUN']

        tr = re.findall("<tr(.*?)/tr>",s,re.DOTALL)

        td = tr[0]
        txt = re.findall('>(.*?)</td>',td)
        tempth = [i for i in txt[2:]]

        td = tr[1]
        txt = re.findall('>(.*?)</td>',td)
        tempth2 =  [i for i in txt[1:]]
        theoryTime = {ind:f'{dat1}-{dat2}' for ind,(dat1,dat2) in enumerate(zip(tempth,tempth2))}

        td = tr[2]     
        txt = re.findall('>(.*?)</td>',td)
        tempth = [i for i in txt[2:]]

        td = tr[3]     
        txt = re.findall('>(.*?)</td>',td)
        tempth2 =  [i for i in txt[1:]]
        labTime = {ind:f'{dat1}-{dat2}' for ind,(dat1,dat2) in enumerate(zip(tempth,tempth2))}


        JSONparse = []
        for ind in range(4,len(tr),2):
            td = re.findall('>(.*?)</td>',tr[ind])
            th,lb = [],[]
            for ind2,txt in enumerate(td[2:]):
                if txt.count('-')>2:
                    splt = txt.split('-')
                    dat = '-'.join([splt[lin] for lin in [1,3,4]]) 
                    code, name = r[dat]
                    th.append([ind2, theoryTime[ind2], dat+'-'+code, name,'th'])

            td = re.findall('>(.*?)</td>',tr[ind+1])
            for ind2,txt in enumerate(td[1:]):
                if txt.count('-')>2:
                    emptyCheck = 0
                    splt = txt.split('-')
                    dat = '-'.join([splt[lin] for lin in [1,3,4]]) 
                    code, name = r[dat]
                    lb.append([ind2, labTime[ind2], dat+'-'+code, name,'lb'])
            lb = processLab(lb)
            JSONformat.append({'day':day[ind//2-2], 'class':sorted(th + lb)})

        if emptyCheck:
            raise ValueError('Empty Data')
      
        return json.dumps({'routine':JSONformat, 'response':'OK'})
    except:
        modifyExp()
        raise Exception('error in RoutineParse')


##def routineParse(s):
##    try:        
##        courseTable = re.search("<table class=\"table\"(.*?)<\/table>",s,re.DOTALL).group(1)
##        courseCol  = re.findall('#3c8dbc;vertical-align: middle;text-align: left;\">(.*?)</td>', courseTable)
##        lis = []
##        emptyCheck = 1 
##        for i in courseCol:
##            temp = i.split(' - ')
##            lis.append([temp[0],temp[1]])
##        # lis contains names of subject and subject code as it is in the table // list
##
##        classInfo= re.findall('<p style=\"margin: 0px;\">(.*?)</p>',courseTable)
##        r = {lis[i//9][0]+'-'+classInfo[i:i+8][6]: [classInfo[i:i+8][4][-4:], lis[i//9][1]] for i in range(0,len(classInfo),9)}
##        # r contains subject code and roomno mapped with classno and subject name // dict
##
##        s = re.search("<table id=\"timeTableStyle\"(.*?)<\/table>",s,re.DOTALL).group(1)
##        JSONformat = []
##        ind =0
##        l,m,index = [],[],[]
##        cnt,init =1,1
##        day =['MON','TUE','WED','THU','FRI','SAT','SUN']
##
##        for i in range(len(day)):
##            index.append(s.find(day[i]))
##        index.append(len(s))
##        # index contains the indexno of string starting that day
##
##        while(s.find("</td",ind)>0):
##            ind = s.find("</td",ind)
##            ind1 = ind-(40-s[ind-40:ind].find('>'))
##
##            if(ind-ind1>10):
##                l.append([cnt,s[ind1+1:ind]])
##            cnt+=1
##            ind=ind+150
##            if ind>index[init]:
##                init+=1
##                m.append(l)
##                l=[]
##        for ind,i in enumerate(m):
##            lab =[]
##            theory =[]
##            for j in i:
##                tup= r['-'.join([j[1].split('-')[inlist] for inlist in [1,-2,-1]])]
##                clsno = '-' + tup[0]
##                k = j[0]%29
##                if k<=15 and k>0:
##                    k=k-2
##                    theory.append([k,j[1]+clsno, tup[1], 'th'])
##                if k>15:
##                    k=k-16
##                    lab.append([k,j[1]+clsno, tup[1], 'lb'])
##                if k==0:
##                    k=13
##                    theory.append([k,j[1]+ clsno], tup[1], 'th')
##            netDayClass = sorted(lab+theory)
##            if emptyCheck and (emptyCheck -1+ len(netDayClass)):
##                emptyCheck = 0
##            JSONformat.append( {'day': day[ind],'class': netDayClass})
##
##        if emptyCheck:
##            raise ValueError('Empty Data')
##        
##        return {'routine' : JSONformat, "response" : 'OK'}
##            
##    except:
##        modifyExp()
##        raise Exception('error in routineParse')

def gradelistParse(s):
    gradeList = []
    creditCalc= []
    try:
        s = s.replace('\r','').replace('\t','')
        ind0 = s.index('Effective Grades')
        ind1 = s.index('Student fails to clear one or more components of a course',ind0)
        table  = re.findall('<tr class="tableContent">(.*?)</tr>',s[ind0:ind1],re.DOTALL)
        for i in table:
            td = re.findall('>(.*?)</td>',i)
            gradeList.append([td[1],td[2],td[4],td[5]])

        ind0= s.index('Credits Earned',ind1)
        ind1 = s.index('Basket Details',ind0)
        table  = re.findall('<tr class="tableContent">(.*?)</tr>',s[ind0:ind1],re.DOTALL)
        for i in table:
            td = re.findall('>(.*?)</td>',i)
            creditCalc.append(td)
        ind0 = s.index('N Grades',ind1)
        table = re.findall('<tr class="tableContent">(.*?)</tr>',s[ind0:],re.DOTALL)
        for i in table:
            td = re.findall('>(.*?)</td>',i)
            gpaList= td
        if gradeList and creditCalc and gpaList:
            return {'gradeList':gradeList, 'creditCalc':creditCalc, 'gpaList':gpaList, 'response': 'OK'}
        raise ValueError('Empty data')
    except:
        modifyExp()
        raise Exception('error in gradelistParse')
    

def gradecalcParse(s):
    try:
        ind =  s.find('Total Number Of Credits: ')
        totalCredit = int(re.findall('<span>(.*?)</span>',s[ind:ind+100])[0])
        courseTable = re.search("<table class=\"table\"(.*?)<\/table>",s,re.DOTALL).group(1)
        courseCol  = re.findall('#3c8dbc;vertical-align: middle;text-align: left;\">(.*?)</td>', courseTable)
        lis = []
        for i in courseCol:
            temp = i.split(' - ')
            lis.append([temp[0],temp[1]])
        # lis contains names of subject and subject code as it is in the table // list

        classInfo= re.findall('<p style=\"margin: 0px;\">(.*?)</p>',courseTable)

        r = [[lis[i//9][0],lis[i//9][1],classInfo[i+2].split(' ')[-1]] for i in range(0,len(classInfo),9)]
        # r contains subject code and roomno mapped with classno and subject name // dict

        finlist =  []
        gradelist = []
        credit = 0 
        for i in r:
            if i[0]+' - '+i[1] not in finlist:
                finlist.append(i[0]+' - '+i[1])
                gradelist.append(credit)
                credit = int(i[2])
            else:
                credit+=int(i[2])
        gradelist.append(credit)
        
        if sum(gradelist)!= totalCredit:
            raise ValueError('problem in varifying gradelist')

        out = [finlist[i].split(' - ')+ [gradelist[i+1]] for i in range(len(finlist))]
        if totalCredit and out:
            return {'gradeCalc':out ,'totalCredit':totalCredit,"response" : 'OK'}
        raise ValueError('Empty data')
    except:
        modifyExp()
        raise Exception('error in gradecalcParse')


def nameParse(s):
    try:
        ind = s.index('font-weight: bold;">Student')
        name_text = re.findall('<td style="background-color: #f2dede;">(.*?)</td>',s[ind:s.index('</tr>',ind)])
        return name_text[0]
    except:
        modifyExp()
        raise Exception('getName failed')
