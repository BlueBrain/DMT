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
A figure is a graphic with a caption.
"""
from pathlib import Path
import shutil
from dmt.tk.utils.string_utils import paragraphs
from dmt.tk.field import Field, lazyproperty, WithFields

class Figure(WithFields):
    """
    A `Figure` is a graphic with a caption.
    """
    graphic = Field(
        """
        A matplotlib figure, or PDF, PNG...
        """)
    caption = Field(
        """
        A text to go with the graphic.
        """,
        __as__=paragraphs)

    def __init__(self,
            figure,
            caption="No caption provided",
            *args, **kwargs):
        """
        Initialize with graphic as an argument.
        `WithField` provides an `__init__` method that accepts initializer
        arguments as keyword arguments.
        However, with this `__init__` method we cannot pass the graphic as a
        keyword argument.

        We still allow `*args, **kwargs` that will allow `class Figure` to be
        mixed in some other class.
        """
        try:
            graphic = figure.graphic
        except AttributeError:
            graphic = figure
        super().__init__(
            graphic=graphic,
            caption=caption,
            *args, **kwargs)


    def save(self, path, dpi=100):
        """
        Save the figure.
        """
        if isinstance(self.graphic, (str, Path)):
            shutil.copy(self.graphic, path)
            return path
        try:
            return self.graphic.savefig(path, dpi=dpi)
        except AttributeError:
            try:
                return self.graphic.figure.savefig(path, dpi=dpi)
            except AttributeError:
                raise TypeError(
                    "Figure type {} not supported".format(
                        self.graphic.__class__))
        return None
