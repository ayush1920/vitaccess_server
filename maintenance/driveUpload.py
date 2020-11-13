''' Requires
client_secrets.json
credentials.json
settings.yaml

Format -
### client_secrets.json
{"web":{"client_id":"<client_id>","project_id":"vernal-tracer-289101","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"<client_secret>","redirect_uris":["http://localhost:8080/"],"javascript_origins":["http://localhost:8080"]}}

### credentials.json
{"access_token": "<access_token>", "client_id": "<client_id>", "client_secret": "<client_secret>", "refresh_token": "<refresh_token>", "token_expiry": "2020-10-02T09:43:19Z", "token_uri": "https://oauth2.googleapis.com/token", "user_agent": null, "revoke_uri": "https://oauth2.googleapis.com/revoke", "id_token": null, "id_token_jwt": null, "token_response": {"access_token": "<access_token>", "expires_in": 3599, "scope": "https://www.googleapis.com/auth/drive.install https://www.googleapis.com/auth/drive", "token_type": "Bearer"}, "scopes": ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.install"], "token_info_uri": "https://oauth2.googleapis.com/tokeninfo", "invalid": false, "_class": "OAuth2Credentials", "_module": "oauth2client.client"}

### settings.yaml

client_config_backend: file
client_config_file: maintenance/client_secrets.json
client_config:
    client_id: <client_id>
    client_secret: <client_secret>

save_credentials: True
save_credentials_backend: file
save_credentials_file: maintenance/credentials.json

get_refresh_token: True

oauth_scope:
    - https://www.googleapis.com/auth/drive
    - https://www.googleapis.com/auth/drive.install
'''

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
import os
import shutil
import telegram.bot as tgbot

def writeLog(data):
    with open('logs/maintenance/driveInfo.log','a+') as f:
        f.write(str(datetime.now()) +' '+ data+'\n')

def writeFolderData(title, idd):
    with open('database/backuplist.txt','w+') as f:
        data = f.read()
        if not data:
            data = '{}'
        folderList = eval(data)
        if 'dict' not in str(type(folderList)):
            raise Exception('Data type of folderList not "LIST"')
        folderList[title] = idd
        f.write(str(folderList))
    writeLog('FOLDER DATA LOGGED')
            
def getFolderID(title):
    if not os.path.isfile('database/backuplist.txt'):
        return ''
    with open('database/backuplist.txt','r') as f:
        data = f.read()
    if not data:
        return ''
    else:
        data = eval(data)
        ID = data.get(title,'')
        return ID

def authenticate():
    gauth = GoogleAuth(settings_file="maintenance/settings.yaml")
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def createFolder(name, drive, skip):
    if skip:
        ID =''
    else:
        ID = getFolderID(name)
    if not ID:
        folder_metadata = {
        'title' : name,
        'mimeType' : 'application/vnd.google-apps.folder'}
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        writeLog(f'{folder["title"]}: {folder["id"]}')
        writeFolderData(folder['title'], folder['id'])
        return folder['id']
    writeLog(f'Folder Exists: {name}: {ID}')
    return ID

def copyFiles():
    lis = os.listdir('database')
    for filename in lis:
        shutil.copy(f'database/{filename}', 'backup')
    
def backup(skip=False):
    tgbot.bot.send_message(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BACKUP STARTED')
    drive  =  authenticate()
    date = '-'.join(str(datetime.date(datetime.now())).split('-')[::-1])
    folderID = createFolder(date, drive, skip)
    copyFiles()
    lis = os.listdir('backup')
    for filename in lis:
        fileUpload = drive.CreateFile({'parents': [{'id': folderID}]})
        fileUpload['title'] = filename 
        fileUpload.SetContentFile(f'backup/{filename}')
        try: fileUpload.Upload()
        except Exception as e:
            if skip: raise 'Exception in backup'
            if 'File not found' in str(e): return backup(True)
            
    writeLog(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BACKUP COMPLETED')
    tgbot.bot.send_message(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: BACKUP ENDED')
    
    
