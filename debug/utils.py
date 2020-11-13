import os

debugPrintCode = {'vtop':1,'moodle':2}

def checknCreate(pth):
    #preprocess path
    splitter = '/'
    if pth.count('\\'):
        if pth.count('/'):
            raise RuntimeError('Different path splitter used')
        splitter = '\\'

    lis = pth.split(splitter)
    # remove filename if in path
    if lis[-1].find('.') != -1:
        lis = lis[:-1]

    current = '/'
    for name in lis:
        if not os.path.exists(f'.{current}{name}'):
            os.mkdir(f'.{current}{name}')
        current+= name+'/'
