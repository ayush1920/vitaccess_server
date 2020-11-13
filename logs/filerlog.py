def printLog(errorCode):
    with open('debug.log','r',encoding='utf-8') as f:
        find = True
        for line in f:
            if find and str(errorCode) in line:
                 find = False
            if not find:
                if line[:5] == '-----':
                    find = True
                    continue
                print(line)
