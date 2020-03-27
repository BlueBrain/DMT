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
A phenomenon is anything that manifests itself, such as an observable, or an
event.
A phenomenon may be described by a system of information related to matter,
energy, or spacetime.
"""

from ..utils.string_utils import make_label, make_name
from ..field import Field, lazyproperty, WithFields

class Phenomenon(WithFields):
    """
    A `Phenomenon` is an observable fact or event, that can be measured.
    """

    name = Field(
        """
        Representation of this `Phenomenon` in a few words.
        """,
        __type__=str,
        __examples__=[
            "Cell Density",
            "Inhibitory Excitatory Ratio"])
    description = Field(
        """
        A text-book description of this Phenomenon.
        """,
        __type__=str)

    group = Field(
        """
        Some phenomena form a group. For example we can group cell-density,
        inhibitory-ratio, synapse density, into composition phenomena.
        """,
        __required__=False)


    def __init__(self,
            name,
            description,
            *args, **kwargs):
        """
        Initialize Me
        """
        super().__init__(
            name=name,
            description=description,
            *args, **kwargs)
       
        if "group" not in kwargs:
            self.group = self.label

    @lazyproperty
    def label(self):
        """
        Convert the given name to a label
        """
        return make_label(self.name)

    @lazyproperty
    def title(self):
        """
        Just another word for `name`.
        """
        return self.name

    @lazyproperty
    def __hash__(self):
        """
        All `Phenomenon`s with the same label and description are equivalent.
        """
        return hash(
            "{} {}".ormat(
                self.label,
                make_name(self.description)))

    def __eq__(self, other):
        """
        Does self equals other?
        """
        return self.__hash__ == other.__hash__

    def __repr__(self):
        """
        Pretty print.
        """
        r = "Phenomenon\n\tname: {}\n\t description: {}\n"\
            .format(
                self.name,
                self.description)








