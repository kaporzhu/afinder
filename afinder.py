# -*- coding:utf-8 -*-
"""
Afinder library
~~~~~~~~~~~~~~~~~~~~~
Afinder stands for attribute finder.
Afinder is an object attr or method find library, written in Python.
usage:
   >>> import afinder
   >>> afinder.search_method(obj, 'something')
   ['obj.attribute.something', 'obj.attribute.moha:"something is here"']
:copyright: (c) 2016 by Kapor Zhu.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'afinder'
__version__ = '0.0.1'
__author__ = 'Kapor Zhu'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Kapor Zhu'

import inspect
import re


BASIC_TYPES = (str, unicode, basestring, int, long, float, complex, tuple, list, set)


def _walk_dict(dictionary, base_path=None):
    for key, value in dictionary.iteritems():
        path = '{}.{}'.format(base_path, key)
        if isinstance(value, BASIC_TYPES):
            yield path, key, value
        elif isinstance(value, dict):
            yield path, key, None
            for p, k, v in _walk_dict(value, path):
                yield p, k, v
        else:
            # class instance
            yield path, key, None
            value.__name__ = key
            for p, k, v in _walk_object(value, path):
                yield p, k, v


def _walk_object(obj, base_path=None):
    base_path = '{}.{}'.format(base_path, obj.__name__) if base_path else obj.__class__.__name__
    for attr_name in dir(obj):
        if attr_name.startswith('__'):
            continue
        attr_value = getattr(obj, attr_name)
        path = '{}.{}'.format(base_path, attr_name)
        if isinstance(attr_value, BASIC_TYPES):
            yield path, attr_name, attr_value
        elif isinstance(attr_value, dict):
            yield path, attr_name, None
            for p, k, v in _walk_dict(attr_value, path):
                yield p, k, v
        elif inspect.isclass(attr_value):
            pass
        else:
            # class instance
            yield path, attr_name, None
            attr_value.__name__ = attr_name
            for p, k, v in _walk_object(attr_value, path):
                yield p, k, v


def afind(obj, text):
    assert obj, 'obj is required'
    assert text, 'text is required'
    text = str(text)
    text_re = re.compile(text.lower(), re.I)
    paths = []
    for path, name, value in _walk_object(obj):
        if text_re.search(name):
            paths.append(path)
        elif value and text_re.search(str(value)):
            paths.append('{}:"{}"'.format(path, value))
    return paths
