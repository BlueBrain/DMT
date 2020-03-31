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
Statistical utilities.
"""

from abc import abstractmethod
from dmt.tk.field import Field, LambdaField, ABCWithFields

class Statistics(ABCWithFields):
    """
    Base class to obtain statistics for data.
    """
    evaluator = Field(
        """
        A callable that accepts measurement data and returns a statistical
        summary, for example, as a `pandas.DataFrame`.
        This attribute may also be implemented as a method in a subclass.
        """)
    story = Field(
        """
        Description of the statistical method used.
        """,
        __default_value__="Not Provided")

    def __init__(self, evaluator, **kwargs):
        """..."""
        super().__init__(
            evaluator=evaluator,
            **kwargs)

    def __call__(self, *args, **kwargs):
        """..."""
        return self.evaluator(*args, **kwargs)

from .distributions import *
