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
Tools to help analyze.

And essential imports
"""
import os

COUNTERBASE = int(os.environ.get("COUNTERBASE", "100"))
def count_number_calls(LOGGER):
    """decorate..."""
    def decorator(method):
        method.n_calls = 0
        def _decorated(*args, **kwargs):
            result = method(*args, **kwargs)
            method.n_calls += 1
            if method.n_calls % COUNTERBASE == 0:
                LOGGER.info(
                    """{} call count : {}""".format(
                        method.__name__,
                        method.n_calls))
            return result
        return _decorated
    return decorator

from .pathway_measurement import PathwayMeasurement
