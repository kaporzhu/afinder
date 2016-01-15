# -*- coding:utf-8 -*-
"""
Afinder library
~~~~~~~~~~~~~~~~~~~~~
Afinder stands for attribute finder.
Afinder is an object attr or method find library, written in Python.
usage:
   >>> from afinder import afind
   >>> afind(obj, 'something')
   ['obj.attribute.something', 'obj.attribute.moha:something is here']
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

BASIC_TYPES = (str, unicode, basestring, int, long, float, complex, set)


def _walk(obj):
    visited_ids = set()
    visited_ids.add(id(obj))
    fields = [('', name, value) for name, value in inspect.getmembers(obj)]
    while fields:
        next_level_fields = []
        for path, name, value in fields:
            if name.startswith('_') or inspect.isclass(value) or inspect.ismodule(value):
                continue
            path = '{}.{}'.format(path, name)
            if isinstance(value, BASIC_TYPES):
                yield path, name, value
            else:
                yield path, name, None
                if not inspect.ismethod(value) and id(value) not in visited_ids:
                    if isinstance(value, (list, tuple)):
                        next_level_fields.extend([(path, str(i), v) for i, v in enumerate(value)])
                    elif isinstance(value, dict):
                        next_level_fields.extend([(path, str(k), v) for k, v in value.iteritems()])
                    else:
                        try:
                            iter(value)
                            # iterable
                            next_level_fields.extend([(path, str(i), v) for i, v in enumerate(value)])
                        except:
                            next_level_fields.extend([(path, n, v) for n, v in inspect.getmembers(value)])
                    visited_ids.add(id(value))
        fields = next_level_fields


def afind(obj, text):
    assert obj, 'obj is required'
    assert text, 'text is required'
    text = str(text)
    text_re = re.compile(text.lower(), re.I | re.M)
    paths = []
    for path, name, value in _walk(obj):
        if text_re.search(name):
            paths.append(path)
        elif value:
            try:
                if isinstance(value, basestring):
                    value = value.encode('utf-8', 'ignore')
                else:
                    value = str(value)

                if text_re.search(value):
                    paths.append('{}:{}'.format(path, value.replace('\n', ' ')))
            except:
                pass
    return paths
