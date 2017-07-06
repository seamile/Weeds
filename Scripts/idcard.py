#!/usr/bin/env python
# coding: utf8

import sys


def get_check_code(id_code):
    s = 0
    weight = lambda i: (1 << (17 - i)) % 11
    for i, a in enumerate(id_code[:-1]):
        s += int(a) * weight(i)
    n = (12 - s % 11) % 11

    return 'X' if n == 10 else str(n)


def convert_id_code(id_code):
    if isinstance(id_code, (list, tuple)):
        id_code = ''.join(i for i in id_code)
    elif isinstance(id_code, bytes):
        id_code = id_code.decode('utf8')
    return id_code.upper()


def check_id(id_code):
    if not isinstance(id_code, (str, bytes, list, tuple)):  # type check
        raise TypeError('Type of the id code is wrong')
    elif len(id_code) != 18:                                # length check
        raise ValueError('Length of the id code is invalid')
    else:
        id_code = convert_id_code(id_code)
        if id_code[-1] not in '0123456789X':
            raise ValueError('Check code is invalid')

    check_code = get_check_code(id_code)
    return check_code == id_code[-1]


def generate_id():
    _input = input if sys.version_info.major > 2 else raw_input
    _input('请输入出生年、月、日 ( 格式: 1980-01-02): ')
    _input('请选择省份: ')
    _input('请输入出生年: ')
