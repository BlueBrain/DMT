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
A quantity is a hypothetically measurable amount of something.
Quantity combines a number with a Unit.
A Quantity has a unique physical-dimension.
"""

from ..field import Field, WithFields
from .unit import Unit

class Quantity(WithFields):
    """
    Quantity combines a number with a Unit.
    """
    amount = Field(
        """
        A number that tells about the amount of this quantity with respect
        to it's associated unit of measurement.
        """,
        __type__=(int, float))
    unit_of_measurement = Field(
        """
        Unit used to measure this quantity.
        """,
        __type__=Unit)
