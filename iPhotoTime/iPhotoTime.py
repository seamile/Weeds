#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re
import sys
import datetime


def get_create_time_from_mtime(fullname):
    timestamp = os.path.getmtime(fullname)
    dtime = str(datetime.datetime.fromtimestamp(timestamp))
    return dtime.replace('-', ':')


def get_create_time_from_filetext(fullname):
    pattern = re.compile(r'\d\d\d\d:[01]\d:[0-3]\d\ [0-2]\d:[0-5]\d:[0-5]\d')
    with open(fullname, 'r') as imgfile:
        filetext = imgfile.read()
        times = pattern.findall(filetext)
        if times:
            return min(times)


def main(photo_dir):
    if photo_dir[-1] == '/':
        photo_dir = photo_dir[:-1]
    print("The photo's directory is: %s" % photo_dir)

    for fname in os.listdir(photo_dir):
        if not fname.startswith('IMG_'):
            continue

        fullname = os.path.join(photo_dir, fname)

        # get create time
        use_mtime = False
        if fname.upper().endswith('.MOV'):
            create_time = get_create_time_from_mtime(fullname)
            use_mtime = True
        else:
            create_time = get_create_time_from_filetext(fullname)
            if not create_time:
                create_time = get_create_time_from_mtime(fullname)
                use_mtime = True

        # generate new file name
        create_date = create_time[:10].replace(':', '')
        new_name = '%s_%s' % (create_date, fname)
        new_full_name = os.path.join(photo_dir, new_name)

        # rename
        ''
        info = 'Change \033[1;32m%s\033[0m to \033[1;33m%s\033[0m' % (fname, new_name)
        if use_mtime == True:
            info += ' (\033[31muse mtime\033[0m)'
        print(info)
        os.rename(fullname, new_full_name)


if __name__ == '__main__':
    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        photo_dir = sys.argv[1]
    else:
        print('Please give the photo directory.')
        sys.exit(1)
    main(photo_dir)
