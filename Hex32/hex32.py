#!/usr/bin/env python
# -*- coding: utf-8 -*-

CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~_'

MAPPING = {'0': 0x00, '1': 0x01, '2': 0x02, '3': 0x03,
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
           'i': 0x2c, 'j': 0x2d, 'k': 0x2e, 'l': 0x2f,
           'm': 0x30, 'n': 0x31, 'o': 0x32, 'p': 0x33,
           'q': 0x34, 'r': 0x35, 's': 0x36, 't': 0x37,
           'u': 0x38, 'v': 0x39, 'w': 0x3a, 'x': 0x3b,
           'y': 0x3c, 'z': 0x3d, '~': 0x3e, '_': 0x3f}  # 64


def fast_encode(num_10, base):
    acc = ''
    shift = {2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6}[base]
    mask = 2 ** shift - 1
    while num_10 > 0:
        i = num_10 & mask
        acc = CHARS[i] + acc
        num_10 >>= shift
    return acc


def fast_decode(num_x, base):
    return int(num_x, base)


def common_encode(num_10, base):
    acc = ''
    while num_10 > 0:
        num_10, mod = divmod(num_10, base)
        acc = CHARS[mod] + acc
    return acc


def common_decode(num_x, base):
    num_10 = 0
    for i, n in enumerate(num_x[::-1]):
        num_10 += MAPPING[n] * base ** i
    return num_10


def hex32(num_10):
    '''dec -> base_32'''
    return fast_encode(num_10, base=32)


def int32(num_32):
    '''base_32 -> dec'''
    return int(num_32, base=32)


def hex36(num_36):
    return common_encode(num_36, base=36)


def int36(num_36):
    return int(num_36, base=36)


def hex62(num_10):
    '''dec -> base_62'''
    return common_encode(num_10, base=62)


def int62(num_62):
    '''base_62 -> dec'''
    return common_decode(num_62, base=62)


def hex64(num_10):
    '''dec -> base_64'''
    return fast_encode(num_10, base=64)


def int64(num_64):
    '''base_64 -> dec'''
    return common_decode(num_64, base=64)


if __name__ == "__main__":
    import random
    a = random.getrandbits(150)
    # a = 752038842036191637862587705727100826138273732
    print('Number is %d\n' % a)

    b = hex32(a)
    print('10 -> 32: %s' % b)
    c = int32(b)
    print('32 -> 10: %d %s= a' % (c, '=' if c == a else '!'))
    print('----')

    b = hex36(a)
    print('10 -> 36: %s' % b)
    c = int36(b)
    print('36 -> 10: %d %s= a' % (c, '=' if c == a else '!'))
    print('----')

    b = hex62(a)
    print('10 -> 62: %s' % b)
    c = int62(b)
    print('62 -> 10: %d %s= a' % (c, '=' if c == a else '!'))
    print('----')

    b = hex64(a)
    print('10 -> 64: %s' % b)
    c = int64(b)
    print('64 -> 10: %d %s= a' % (c, '=' if c == a else '!'))
