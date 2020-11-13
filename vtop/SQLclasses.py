from sharedDB_tpl import dbvtop as db

class users(db.Model):
    regno = db.Column(db.String(10), primary_key = True)
    passwrd = db.Column(db.String(20))
    cookies = db.Column(db.String(400))
    time = db.Column(db.Integer)
    name = db.Column(db.String(25))
    marksTime = db.Column(db.Integer)

    def __init__(self, regno, passwrd, cookies, time, name, marksTime):
        self.regno = regno
        self.passwrd =passwrd
        self.cookies = cookies
        self.time = time
        self.name = name
        self.marksTime = marksTime


class marks(db.Model):
    regno = db.Column(db.String(10), primary_key = True)
    marks = db.Column(db.String(10000))
    def __init__(self, regno, marks):
        self.regno = regno
        self.marks = marks

