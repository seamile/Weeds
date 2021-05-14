#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
类似 namedtuple, 可控制属性是否只读。参考OrderDict
'''

from new import classobj



def nameddict(typename, field_names, readonly=True):
    """Returns a new subclass of dict with named fields.

    >>> Point = nameddict('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)

    """    def __init__
    def __
    return classobj(typename, (dict,), {
                    '__setattr__':
                    })
