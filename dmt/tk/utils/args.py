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
Utilities to handle arguments.
"""
import functools

def require_only_one_of(**kwargs):
    """
    Require only one argument among a sequence.
    """
    assert kwargs, "Nothing passed."
    assert sum(value is not None for value in kwargs.values()) == 1,\
        "Expected one and only one argument among: {}"\
        .format([key for key in kwargs.keys()])




