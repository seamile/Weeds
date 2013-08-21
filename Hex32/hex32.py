#!/usr/bin/env python
# -*- coding: utf-8 -*-

MAPPING32 = {0x00: '0', 0x01: '1', 0x02: '2', 0x03: '3',
             0x04: '4', 0x05: '5', 0x06: '6', 0x07: '7',
             0x08: '8', 0x09: '9', 0x0a: 'A', 0x0b: 'B',
             0x0c: 'C', 0x0d: 'D', 0x0e: 'E', 0x0f: 'F',
             0x10: 'G', 0x11: 'H', 0x12: 'I', 0x13: 'J',
             0x14: 'K', 0x15: 'L', 0x16: 'M', 0x17: 'N',
             0x18: 'O', 0x19: 'P', 0x1a: 'Q', 0x1b: 'R',
             0x1c: 'S', 0x1d: 'T', 0x1e: 'U', 0x1f: 'V'}

MAPPING10 = {'0': 0x00, '1': 0x01, '2': 0x02, '3': 0x03,
             '4': 0x04, '5': 0x05, '6': 0x06, '7': 0x07,
             '8': 0x08, '9': 0x09, 'A': 0x0a, 'B': 0x0b,
             'C': 0x0c, 'D': 0x0d, 'E': 0x0e, 'F': 0x0f,
             'G': 0x10, 'H': 0x11, 'I': 0x12, 'J': 0x13,
             'K': 0x14, 'L': 0x15, 'M': 0x16, 'N': 0x17,
             'O': 0x18, 'P': 0x19, 'Q': 0x1a, 'R': 0x1b,
             'S': 0x1c, 'T': 0x1d, 'U': 0x1e, 'V': 0x1f}


def convert_to_32(num_10):
    '''转换为 32 进制'''
    a = num_10 & 0x1f
    b = MAPPING32[a]
    num_10 >>= 5
    while num_10 > 0:
        a = num_10 & 0x1f
        b += MAPPING32[a]
        num_10 >>= 5
    return b[::-1]


def convert_to_10(num_32):
    '''转换为 10 进制'''
    num_10 = 0
    for i, n in enumerate(num_32[::-1]):
        num_10 += MAPPING10[n] * 32 ** i
    return num_10


if __name__ == "__main__":
    a = 12345
    b = convert_to_32(a)
    print('10 -> 32: %d  %s' % (a, b))
    c = convert_to_10(b)
    print('32 -> 10: %s  %d' % (b, c))
