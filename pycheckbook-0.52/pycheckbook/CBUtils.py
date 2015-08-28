#!/usr/bin/python

import string
def string_limit(str,limit):
    if not str:
        pass
    elif len(str) > limit:
        str = str[:limit]
    return str

