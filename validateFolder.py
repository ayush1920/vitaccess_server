import os

def createFolder(location):
    if not os.path.isdir(location):
        os.path.mkdir(location)


createFolder('backup')
createFolder('database')
createFolder('static')
createFolder('templates')
