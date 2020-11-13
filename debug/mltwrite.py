# -- last modified 27/08/20 --

import threading
from queue import Queue
import io

class mltFileWriter:
    def __init__(self, name,mode = 'a+', enc = 'utf-8'):
        self.name = name
        self.mode = mode
        self.enc = enc
        self.queue = Queue()
        self.isRunning = False
        self.openfile()
        
    def openfile(self):
        self.file = io.open(self.name, mode = self.mode, encoding = self.enc)

    def worker(self):
        self.isRunning = True
        while True:
            if self.queue.empty(): break
            text = self.queue.get()
            self.writeData(text)
            self.queue.task_done()
        self.isRunning = False
            
    def closefile(self):
        if self.file.closed:
            return
        self.file.close()

    def write(self, text):
        self.queue.put(text)
        if not self.isRunning:
            threading.Thread(target = self.worker, daemon=True).start()
            
    def writeData(self, text):
        if self.file.closed:
            self.openfile()
        self.file.write(str(text))
        self.file.flush()

    def isFileOpen(self):
        return not self.file.closed

    def flush(self):
        if not self.isRunning:
            self.worker()
            
    
        
        
    
