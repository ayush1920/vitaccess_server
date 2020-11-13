from sharedDB_tpl import dbvtop
from sharedDB_tpl import dbmoodle
import socket
import requests.packages.urllib3.util.connection as urllib3_cn


def initializeDB():
    from moodle.SQLclasses import users, group
    from vtop.SQLclasses import users
    dbvtop.create_all()
    dbmoodle.create_all()


# monkeypatching to force requests to use TCP/IP4 for faster call
def forceTCP4():
    def allowed_gai_family():
        return socket.AF_INET
    urllib3_cn.allowed_gai_family = allowed_gai_family
