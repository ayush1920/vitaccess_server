from random import randint
from moodle.SQLclasses import users
from threading import Thread
import zlib

moduleCode = 2


def randomIDGenerator():
    while True:
        _id = ''
        for count in range(8): _id +=  chr(randint(97,122))
        if not users.query.filter_by(_id = _id ).first():
            return _id

def data2hash(param1, param2):
    def lenCheck(param):
        if len(param)>10:
            return param[:10]
        while len(param) < 10:
            param+='4'
        return param

    byte1, byte2 = bytes(param1, 'utf-8'), bytes(param2, 'utf-8')
    hashed1, hashed2 = lenCheck(str(zlib.crc32(byte1))), lenCheck(lenCheck(str(zlib.crc32(byte2))))
    hashp1p2 = ''
    for i in range(20):
        if i%2==0:
            hashp1p2+=hashed1[i//2]
        else:
            hashp1p2+=hashed2[i//2]
    fin = ''
    for i in range(0,20,2):
        hexx = int(hashp1p2[i:i+2])%16
        if hexx>9:
            hexx = chr(hexx+87)
        fin +=str(hexx)
    hash_ = lenCheck(str(zlib.crc32(bytes(fin, 'utf-8'))))
    fin = fin[:8]
    crc32_p2_hash = ''
    for i in range(20):
        if i%2==0:
            crc32_p2_hash += hashed2[i//2]
        else:
            crc32_p2_hash += hash_[i//2]

    for i in range(0,20,2):
        hexx = int(crc32_p2_hash[i:i+2])%16
        if hexx>9:
            hexx = chr(hexx+87)
        fin +=str(hexx)
    fin = fin[0:16]
    return fin

def chunkDownloader(request, maxlength):
    for chunk in request.iter_content(maxlength):             
        data = chunk
        break
    return data.decode('utf-8')

class ThreadWithReturn(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

