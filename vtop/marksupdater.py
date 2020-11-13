# -- last modified 08/09/20 --

import threading
import io
import os
import debug.utils as utils
from debug.serverlog import consoleLog
import sys

class mrxUpdate:
    def __init__(self,name):
        self.name = name
        self.lock = threading.Lock()
        self.marks = {}
        self.initialise()
        self.writeMarks()

            
    def initialise(self):
        if not os.path.isfile(self.name):
            utils.checknCreate(self.name)
        else:
            f = open(self.name,'r')
            try:
                self.marks = eval(f.read())
                f.close()
            except:
                f.close()
                
    def writeMarks(self):
        self.writeData(str(self.marks))
           
    def closefile(self):
        if self.file.closed:
            return
        self.file.close()

    def isFileOpen(self):
        return not self.file.closed

    def update(self, marksDict):
        try:
            # marksDict Example - {780: {2: 9.7}, 1624: {1: 25.0, 2: 9.7}}
            # savedmarks Example - {780:{2:[10.7,12]}}
            with self.lock:
                for i in marksDict:
                    for j in marksDict[i]:
                        marks = marksDict[i][j]
                        submarks = self.marks.get(i,{}).get(j,[])
                        if submarks:
                            avg, total = submarks
                            self.marks[i][j] = [round((avg*total+marks)/(total+1),2), total+1]
                        else:
                            if self.marks.get(i,False):
                                self.marks[i][j] = [marks,1]
                            else:
                                self.marks[i] = {j:[marks,1]}
                self.writeData(str(self.marks))
                return True,''
        except:
            return False,sys.exc_info()
            
    def getAvg(self, queryDict):
        # queryDict format {780: [1], 806: [1], 889: [1], 890: [1], 891: [1]}
        cpy = self.marks
        finlist = []
        for i in queryDict:
            lis = []
            submarks = cpy.get(i,{})
            for j in queryDict[i]:
                lis.append(submarks.get(j,[]))
            finlist.append(lis)
        return finlist

    def writeData(self, text):
        self.file = open(self.name, "w")
        self.file.seek(0)
        self.file.write(text)
        self.file.truncate()
        self.file.close()

avgClass = mrxUpdate('./database/avg.dat')
