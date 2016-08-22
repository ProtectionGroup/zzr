import os
import re
import datetime

def getserial():
    # Extract serial from cpuinfo file
    id = ''
    try:
        with open('/sys/class/net/eth0/address', 'r') as f:
            number = f.readline()
        a = ''.join(number.split(':'))
        id = a.strip()
        #result = re.findall(r'[0-9]\d+',id )
        res = ''
        for i in id:
            res +=str(ord(i))
    except BaseException:
        getserial()

    return res


if __name__ == '__main__':
    getserial()
