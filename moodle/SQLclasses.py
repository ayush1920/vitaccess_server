from sharedDB_tpl import dbmoodle as db

class users(db.Model):
    __bind_key__ = 'moodle'
    regno = db.Column(db.String(10), primary_key = True)
    passwrd = db.Column(db.String(20))
    moodleID = db.Column(db.Integer)
    cookies = db.Column(db.String(400))
    time = db.Column(db.Integer)
    def __init__(self, regno, passwrd, moodleID, cookies,time):
        self.regno = regno
        self.passwrd =passwrd
        self.moodleID = moodleID
        self.cookies = cookies
        self.time = time
       

class group(db.Model):
    __bind_key__ = 'moodle'
    regno = db.Column(db.String(10), primary_key = True)
    moodleID = db.Column(db.Integer, unique = True)
    groupdata = db.Column(db.String(400))
    shareModule  = db.Column(db.Boolean)
    def __init__(self, regno, moodleID, groupdata,shareModule):
        self.regno = regno
        self.moodleID = moodleID
        self.groupdata = groupdata
        self.shareModule = shareModule
