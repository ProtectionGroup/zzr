#!/bin/bash
cd /home/pi/zzr

	if ps ax | grep check_ftp.py | grep -vq grep
then
        z=1
else
        sudo python /home/pi/zzr/check_ftp.py >/dev/null &
fi
