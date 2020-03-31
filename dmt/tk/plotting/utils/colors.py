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
Utilities to handle colors to plot with.
"""


from collections.abc import Mapping, Callable

class ColorPalette(Mapping):
    """
    A color palette.
    """
    def __init__(self, colors, *args, **kwargs):
        """..."""
        if isinstance(colors, Callable):
            ColorPalette.from_callable(colors, *args, **kwargs)
            return
        if isinstance(colors, dict):
            ColorPalette.from_dict(colors, *args, **kwargs)
            return
        if isinstance(colors, pd.Series):
            ColorPalette.from_dict(colors.to_dict(), *args, **kwargs)
            return
        if isinstance(colors, pd.DataFrame):
            ColorPalette.from_dataframe(colors, *args, **kwargs)
            return
        raise ValueError(
            """
            No handler for colors:
            \t{}
            """.format(colors))

    @classmethod
    def from_callable(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError

    @classmethod
    def from_dataframe(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError
