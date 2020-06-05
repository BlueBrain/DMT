# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Wrap data with meta-data.
"""
import os

DMTPATH = "DMTPATH"

def check_environment(variable, value=None):
    if not value:
        try:
            value = os.environ[variable]
        except KeyError:
            raise RuntimeError(
                """
                Neither was {} provided as an argument,
                nor was it available in the environment.
                """.format(variable))
        return value

from .layer_thickness import\
    LayerThicknessMeasurement,\
    CorticalThicknessMeasurement
