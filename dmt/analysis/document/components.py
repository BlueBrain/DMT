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
Components of a documented analysis.
"""
import json
from ..measurement import Measurement, MeasurementSuite
from .import *


class Section(DocElem):
    @field.cast(Narrative)
    def narrative(self):
        """
        A text that will become the story told in this section.
        """
        raise FieldIsRequired

    @field.cast(Data)
    def data(self):
        """
        Data for this section.
        """
        return NA

    @field.cast(Illustration)
    def illustration(self):
        """
        Illustration for this section.
        """
        return NA

    def save(self, section, path_folder):
        """..."""
        path_section = path_folder.joinpath(section.label)
        try:
            narrative = section.narrative
        except AttributeError:
            narrative = None
        try:
            data = section.data
        except AttributeError:
            data = None
        try:
            illustration = section.illustration
        except AttributeError:
            illustration = None

        if narrative:
            self.narrative.save(narrative, path_section)
        if data:
            self.data.save(data, path_section)
        if illustration:
            self.illustration.save(illustration, path_section)

        for subsection in self.children:
            subsection.save(section.children, path_section)

        return path_section

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        data = self.data(adapter, model, *args, **kwargs)
        return Record(
            title=self.title,
            label=self.label,
            narrative=self.narrative(adapter, model, *args, **kwargs),
            data=data,
            illustration=self.illustration(adapter, model, *args,
                                           data=data, **kwargs))


class Abstract(Section):
    """
    Abstract to an argument, is a `DocElem` but not a section.
    """
    title = "Abstract"
    label = "abstract"

    @field.cast(Narrative)
    def narrative(self):
        """
        A text that will become the story told in this section.
        """
        raise FieldIsRequired

    def __init__(self, narrative, *args, **kwargs):
        """
        Initialize `Abstract` with a story.
        """
        kwargs["narrative"] = narrative
        super().__init__(*args, **kwargs)

    def save(self, abstract, path_folder):
        """
        Save an abstract value computed for some adapter, model. 
        """
        path_abstract = path_folder.joinpath("abstract")
        self.narrative.save(abstract.narrative, path_abstract)

        return path_abstract

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return Record(
            title=self.title,
            label=self.label,
            narrative=self.narrative(adapter, model, *args, **kwargs))


class Introduction(Section):
    """
    Make Section an Introduction
    """
    title = "Introduction"

    def __init__(self, narrative=NA, *args, **kwargs):
        """
        Initialize `Introduction` with a story.
        """
        kwargs["narrative"] = narrative
        super().__init__(*args, **kwargs)


class Methods(Section):
    """..."""
    title = "Methods"
    @field.cast(MeasurementSuite)
    def measurements(self):
        """
        A dict that will be cast to become a `MeasurementSuite`.
        """
        return NA

    def save(self, value, path_folder):
        """
        Save a value of this methods instance evaluated for a given
        adapter, model
        """
        path_methods = super().save(value, path_folder)
        try:
            measurements = value.measurements
        except AttributeError:
            measurements = None
        if measurements:
            with open(path_methods.joinpath("measurements.json"), 'w') as f:
                json.dump(measurements, f)

        return path_methods

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return\
            super().__call__(
                adapter, model, *args, **kwargs
            ).assign(
                measurements=OrderedDict([
                    (l, m.description(adapter, model, *args, **kwargs))
                    for l, m in self.measurements.items()]))


class Results(Section):
    title = "Results"
    pass
