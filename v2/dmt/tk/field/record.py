"""
A record.
"""

import random
from .import Field, WithFields

def Record(**kwargs):
    fields = {
        key: Field("record field {}".format(key))
        for key in kwargs.keys()}
    record_type =\
        type(
            "Record{}".format(random.randint(0, 1000000000)),
            (WithFields,),
            fields)
    return record_type(**kwargs)
