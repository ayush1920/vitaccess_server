import os
import threading
import requests
import json
from datetime import datetime
from debug.utils import checknCreate

class telegram_serverbot():

    def __init__(self):
        self.token = '1152939742:<telegram_api_key>'
        self.base = f'https://api.telegram.org/bot{self.token}/'
        self.counter = 0
        self.counterLimit = 30
        checknCreate('logs/telegram')

        
    def send_message(self, msg):
        if not msg: return False
        url = f"{self.base}sendMessage?chat_id=<chat_id>&text={msg}"
        res = requests.get(url)
        return self.errorLog(res)

    def errorLog(self, res):
        res = json.loads(res.text)
        if res['ok']:return True
        error  = str(res)
        with open('logs/telegram/telegramError.log','a+') as f:
            f.write(f'{"-"*20}\n {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n {error}\n')
        return False

    def uploadFile(self,name):
        url = f"{self.base}sendDocument?chat_id=<chat_id>"
        if not os.path.isfile(name):
            return self.send_message('FILE NOT FOUND')
        res = requests.post(url, files=dict(document = (name, open(name, 'rb'),'text/plain')))
        return self.errorLog(res)
    
    def uploadLog(self, name, error):
        if self.counter > self.counterLimit:
            return
        threading.Thread(target = self.ThreadedUpload, args=(name, error,)).start()
    
    def ThreadedUpload(self, name, error):
        url = f"{self.base}sendDocument?chat_id=<chat_id>"
        try:
            res = requests.post(url, files=dict(document = (name+'.txt', error)))
        except:
            class errorCls:
                def __init__(self):
                    self.text = json.dumps({'ok':False,'response':'CUSTOM: Maybe conenction Error'})
            errorcls = errorCls()
            return self.errorLog(errorcls)
        self.counter+=1
        return self.errorLog(res)

    
    def resetCounter(self):
        self.counter = 0
    
bot = telegram_serverbot()
