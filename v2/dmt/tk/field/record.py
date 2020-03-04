"""
A record.
"""

import random
from .import Field, WithFields

def Record(**kwargs):
    attributes = {
        key: Field("record field {}".format(key))
        for key in kwargs.keys()}

    def __repr__(self):
        return\
            '\n'.join(
                "{}: {}".format(field, repr(value).replace('\n', "; "))
                for field, value in self.field_dict.items())

    attributes["__str__"] = __repr__
    attributes["__repr__"] = __repr__

    record_type =\
        type(
            "Record{}".format(random.randint(0, 1000000000)),
            (WithFields,),
            attributes)
    return record_type(**kwargs)

    

