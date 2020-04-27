# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
A record.
"""

import random
from .import Field, WithFields

def Record(**kwargs):
    attributes = {
        key: Field("record field {}".format(key))
        for key, value in kwargs.items()
        if value is not None}

    def __repr__(self):
        return\
            '\n'.join(
                "{}: {}".format(field, repr(value).replace('\n', "; "))
                for field, value in self.field_dict.items())

    def assign(self, **new_fields):
        """
        Create a new record with additional fields.
        """
        return Record(**self.field_dict, **new_fields)

    attributes["__str__"] = __repr__
    attributes["__repr__"] = __repr__
    attributes["assign"] = assign

    record_type =\
        type(
            "Record{}".format(random.randint(0, 1000000000)),
            (WithFields,),
            attributes)
    return record_type(**kwargs)


