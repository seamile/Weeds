#!/usr/bin/env python

import re
import sys
import datetime

try:
    i = 0
    p = re.compile('(?<=#)\d+(?=\n)')
    with open(sys.argv[1]) as fd:
        for line in fd:
            res = p.findall(line)
            if res:
                tm = str(datetime.datetime.fromtimestamp(int(res[0])))
                i += 1
                sys.stdout.write('\033[35m%4d [%s] \033[0m' % (i, tm))
            else:
                sys.stdout.write(line)
except Exception, e:
    print(e)
