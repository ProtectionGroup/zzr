# -*- coding: utf-8 -*-
import datetime, time
import requests
from get_id import getserial

def register():
    a = getserial()
    r = requests.get('http://glob-control.com/registry.html?rpi_id='+a)
    print r.text
    if r.text != '1':
        date = datetime.datetime.now()
        print r.text
        time.sleep(10)
        register()


if __name__ == '__main__':
    register()
