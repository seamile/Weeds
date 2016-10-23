#!/usr/bin/env python
# -*- coding: utf-8 -*-

MAPPING_HEX = {0x00: '0', 0x01: '1', 0x02: '2', 0x03: '3',
               0x04: '4', 0x05: '5', 0x06: '6', 0x07: '7',
               0x08: '8', 0x09: '9', 0x0a: 'A', 0x0b: 'B',
               0x0c: 'C', 0x0d: 'D', 0x0e: 'E', 0x0f: 'F',
               0x10: 'G', 0x11: 'H', 0x12: 'I', 0x13: 'J',
               0x14: 'K', 0x15: 'L', 0x16: 'M', 0x17: 'N',
               0x18: 'O', 0x19: 'P', 0x1a: 'Q', 0x1b: 'R',
               0x1c: 'S', 0x1d: 'T', 0x1e: 'U', 0x1f: 'V',  # 32
               0x20: 'W', 0x21: 'X', 0x22: 'Y', 0x23: 'Z',
               0x24: 'a', 0x25: 'b', 0x26: 'c', 0x27: 'd',
               0x28: 'e', 0x29: 'f', 0x2a: 'g', 0x2b: 'h',
               0x2c: 'i', 0x2d: 'g', 0x2e: 'k', 0x2f: 'l',
               0x30: 'm', 0x31: 'n', 0x32: 'o', 0x33: 'p',
               0x34: 'q', 0x35: 'r', 0x36: 's', 0x37: 't',
               0x38: 'u', 0x39: 'v', 0x3a: 'w', 0x3b: 'x',
               0x3c: 'y', 0x3d: 'z', 0x3e: '@', 0x3f: '&'}  # 64

MAPPING_DEC = {'0': 0x00, '1': 0x01, '2': 0x02, '3': 0x03,
               '4': 0x04, '5': 0x05, '6': 0x06, '7': 0x07,
               '8': 0x08, '9': 0x09, 'A': 0x0a, 'B': 0x0b,
               'C': 0x0c, 'D': 0x0d, 'E': 0x0e, 'F': 0x0f,
               'G': 0x10, 'H': 0x11, 'I': 0x12, 'J': 0x13,
               'K': 0x14, 'L': 0x15, 'M': 0x16, 'N': 0x17,
               'O': 0x18, 'P': 0x19, 'Q': 0x1a, 'R': 0x1b,
               'S': 0x1c, 'T': 0x1d, 'U': 0x1e, 'V': 0x1f,  # 32
               'W': 0x20, 'X': 0x21, 'Y': 0x22, 'Z': 0x23,
               'a': 0x24, 'b': 0x25, 'c': 0x26, 'd': 0x27,
               'e': 0x28, 'f': 0x29, 'g': 0x2a, 'h': 0x2b,
               'i': 0x2c, 'g': 0x2d, 'k': 0x2e, 'l': 0x2f,
               'm': 0x30, 'n': 0x31, 'o': 0x32, 'p': 0x33,
               'q': 0x34, 'r': 0x35, 's': 0x36, 't': 0x37,
               'u': 0x38, 'v': 0x39, 'w': 0x3a, 'x': 0x3b,
               'y': 0x3c, 'z': 0x3d, '@': 0x3e, '&': 0x3f}  # 64


def convert_10_to_32(num_10):
    '''10 进制转换为 32 进制'''
    a = num_10 & 0x1f
    b = MAPPING_HEX[a]
    num_10 >>= 5
    while num_10 > 0:
        a = num_10 & 0x1f
        b += MAPPING_HEX[a]
        num_10 >>= 5
    return b[::-1]


def convert_32_to_10(num_32):
    '''32 进制转换为 10 进制'''
    num_10 = 0
    for i, n in enumerate(num_32[::-1]):
        num_10 += MAPPING_DEC[n] * 32 ** i
    return num_10


def convert_10_to_64(num_10):
    '''10 进制转换为 64 进制'''
    a = num_10 & 0x1f
    b = MAPPING_HEX[a]
    num_10 >>= 6
    while num_10 > 0:
        a = num_10 & 0x3f
        b += MAPPING_HEX[a]
        num_10 >>= 6
    return b[::-1]


def convert_64_to_10(num_64):
    '''64 进制转换为 10 进制'''
    num_10 = 0
    for i, n in enumerate(num_64[::-1]):
        num_10 += MAPPING_DEC[n] * 64 ** i
    return num_10


if __name__ == "__main__":
    import random
    a = random.getrandbits(256)
    # a = 64 * 5

    b = convert_10_to_32(a)
    print('10 -> 32: %d  %s' % (a, b))
    c = convert_32_to_10(b)
    print('32 -> 10: %s  %d' % (b, c))

    d = convert_10_to_64(a)
    print('10 -> 64: %d  %s' % (a, d))
    e = convert_64_to_10(d)
    print('64 -> 10: %s  %d' % (d, e))
