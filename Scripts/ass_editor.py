#!/usr/bin/env python
# coding: utf8
import re

stime = re.compile('\d{1,2}\:\d\d\:\d\d[,.]\d\d')


def stime_add(strtime, secodes):
    strtime = strtime.replace(',', '.')
    h, m, s = [float(i) for i in strtime.split(':')]
    total = h * 3600 + m * 60 + s + secodes
    s = total % 60
    total -= s
    m = total % 3600
    total -= m
    h = total / 3600
    m = m / 60
    if h < 0 or m < 0 or s < 0:
        return '0:00:00.00'
    else:
        s = '%02d:%02d:%05.2f' % (h, m, s)
        return s


def change_line(line, secodes):
    for s in stime.findall(line):
        line = line.replace(s, stime_add(s, secodes))
    return line


def guess_encoding(text):
    encodings = ['utf8', 'gb18030','gbk', 'gb2312']
    for e in encodings:
        try:
            text.decode(e)
            return e
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("invalid encoding type")


def change_ass(f, secodes):
    with open(f, 'rb') as fp:
        lines = fp.readlines()
    encoding = guess_encoding(lines[0])
    for i, l in enumerate(lines):
        lines[i] = change_line(l.decode(encoding), secodes)
    text = ''.join(lines)
    with open(f, 'w') as fp:
        fp.write(text)


if __name__ == '__main__':
    import sys
    f, secodes = sys.argv[1], sys.argv[2]
    secodes = float(secodes)
    change_ass(f, secodes)
