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
Collection of terms.
"""
from dmt.tk.utils.singleton import Singleton


class TermCollection(Singleton):
    """
    A collection of terms.
    """
    @classmethod
    def make_query(cls, **kwargs):
        """
        Make a query from key-word arguments.
        """
        return {
            label: kwargs[label]
            for label in cls.terms
            if label in kwargs}

    @classmethod
    def filter(cls, **query):
        """
        Filter all the query entries that have value `None`.
        """
        return {
            label: value
            for label, value in query.items()
            if label in cls.terms and value is not None}

