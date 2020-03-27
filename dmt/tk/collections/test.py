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
Test develop collections.
"""
from . import  get_list

def test_get_list():
    """
    Get list should return list from singletons, as well as list-like...
    """
    a_list = get_list("a")
    assert len(a_list) == 1
    assert a_list[0] == "a"

    ab = ['a', 'b']
    ab_list = get_list(*ab)

    assert len(ab_list) == len(ab)
    assert ab_list[0] == ab[0]
    assert ab_list[1] == ab[1]
