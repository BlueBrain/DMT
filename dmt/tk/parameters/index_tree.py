# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Handle multi level columns and indexes.
"""
from collections.abc import Mapping
from collections import OrderedDict
import pandas

def as_nested_dict(row):
    """
    Convert a row containing parameter labels and values to a nested dict.
    A row may be a `pandas.Series` with a multi-level index,
    which when converted to a dict will have tuples as keys.
    """
    type_error = TypeError(
        """
        Parameters label (keys) should either be
        \t1. strings, or
        \t2. non-empty same length tuples of strings. 
        """)

    def _validate(key):
        if not isinstance(key, tuple) and not isinstance(key, str):
            raise type_error
        if isinstance(key, tuple)\
           and not len(key) > 0\
           and not all(isinstance(k, str) for k in key):
            raise type_error
        return True

    def _get_key_length(key):
        _validate(key)
        return len(key) if isinstance(key, tuple) else None

    if isinstance(row, dict):#assuming well formed:
        if not row: #empty dict --- this can be dangerous when unnested
            return row
        assert all(_validate(key) for key in row.keys())
        key_lengths = {
            _get_key_length(key)
            for key in row.keys()}
        if len(key_lengths) != 1:
            raise type_error
        length = key_lengths.pop()
        if length is None:
            return row
        if length == 1:
            return {
                key[0]: value
                for key, value in row.items()}
        zero_level_values = {
            key[0] for key in row.keys()}
        
        def _extract_level_zero(level_value):
            return {
                key[1:] : value
                for key, value in row.items()
                if key[0] == level_value}
        
        return {
            level_value : as_nested_dict(_extract_level_zero(level_value))
            for level_value in zero_level_values}
    
    assert isinstance(row, pandas.Series)
    
    if not isinstance(row.index, pandas.MultiIndex):
        if len(row) == 1 and row.index.values[0] == "":
            return row.values[0]
        if any(key == "" for key in row.index.values):
            raise TypeError(
                """
                `as_nested_dict(...)` cannot unnest a pandas.Series with
                single level index that has an empty string as a key:
                \t{}
                """.format(row))
        return row.to_dict()
    
    zero_level_values = row.index.get_level_values(level=0)
    return {
        level_value: as_nested_dict(row.loc[level_value])
        for level_value in zero_level_values}


def as_unnested_dict(row):
    """
    Take a nested dict, with multiple levels,
    and return a dict with a single level.

    Assumption
    --------------
    The final values in the nested dict `row` are at the same level.
    """
    if not isinstance(row, Mapping):
        return row

    def _get_next_level(value):
        if not isinstance(value, Mapping):
            return value
        else:
            return as_unnested_dict(value)

    def _prepend(key, next_level):
        if not isinstance(next_level, Mapping):
            return [(key, next_level)]
        def _concat(next_level_key):
            return (key, next_level_key)\
                if not isinstance(next_level_key, tuple)\
                   else (key,) + next_level_key
        return list(
            (_concat(next_level_key), value)
            for next_level_key, value in next_level.items())

    return dict(
        flat_key_value_pair
        for key, value in row.items()
        for flat_key_value_pair in _prepend(key, _get_next_level(value)))
