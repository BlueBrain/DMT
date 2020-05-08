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
An analysis' measurement.
An `Analysis` will be that of one or more instances of `Measurement`.
"""

from collections.abc import Mapping
from collections import OrderedDict
import numpy as np
import pandas as pd
from dmt.model import AIBase
from dmt.model.interface import interfacemethod
from dmt.data.observation.measurement import\
    collection as measurement_collection
from dmt.data.observation.measurement.collection import\
    primitive_type, series_type, vector_type, summary_type, multi_type
from dmt.tk.journal import Logger
from dmt.tk.parameters import Parameters
from dmt.tk.field import\
    field, Field,\
    lambdafield, LambdaField,\
    lazyfield,\
    NA, Record,\
    WithFields,\
    FieldIsRequired

from .document import Narrative

class Measurement(WithFields, AIBase):
    """
    All that is needed to make measurement on a model.

    TODO:
    1. In principle attribute `collection` may be implemented as a method
    of a subclass. However, we might have the call method assumes that the 
    implementation returns a `pandas.DataFrame` with a column named `value` 
    that holds the result of the measurement. Changing the column name from
    `value` to the label of this `Measurement` instance will be necessary to
    use the measurement result for plotting...
    """
    label = Field(
        """
        Single word string to name the measurement column.
        """,
        __default_value__="value")
    sample_size = Field(
        """
        Number of repetitions for each set of parameter values.
        """,
        __default_value__=1)

    @field.cast(Narrative)
    def description(self):
        """
        A tagged-template string that describes this `Measurement`.
        """
        return NA

    @field.cast(Parameters)
    def parameters(self):
        """
        An object providing a collection of parameters to measure with.
        This object may be:
        1. Either `pandas.DataFrame`,
        2. or `adapter, model -> Collection<MeasurementParameters>`,
        3. or `dmt.tk.Parameters`.

        You can provide this as a field, or override by implementing this as a
        function in a subclass.
        """
        return None

    @field
    def method(self, *args, **kwargs):
        """
        That makes a measurement.

        You can provide this as a field, or override by implementing this as a
        function in a subclass.
        """
        raise FieldIsRequired

    @field
    def collection(self):
        """
        A policy to collect the measurements over all parameter sets.

        The default value provided below assumes that an individual measurement
        is a primitive data type such as a float, integer, or string.

        You can provide this as a field, or override by implementing this as a
        function in a subclass.
        """
        return measurement_collection.primitive_type

    def __init__(self, measurement, **kwargs):
        """
        Initialize with either keyword arguments,
        1. or a callable
        """
        if callable(measurement):
            kwargs["method"] = measurement
        else:
            try:
                kwargs.update(measurement.field_dict)
            except AttributeError:
                kwargs.update(measurement)
        return super().__init__(**kwargs)

    def collect(self, adapter, model, **kwargs):
        """
        Collect a measurement
        """
        if self.parameters is not None:
            collected =\
                self.collection(
                    (p, self.method(adapter, model, **p, **kwargs))
                    for p in self.parameters(
                            adapter, model,
                            sample_size=self.sample_size,
                            **kwargs
                    )
                )
            try:
                return collected.rename(columns={"value": self.label})
            except:
                return collected
        return self.method(adapter, model, **kwargs)


class MeasurementSuite(Mapping):
    """
    Suite of measurements...
    """
    def __init__(self, measurements):
        """
        measurements :  An `OrderedDict` mapping measurement label to it's
        ~              value / definition / collector.
        """
        self._measurements = OrderedDict([
            (label, Measurement(value))
            for label, value in measurements.items()
        ])

    @property
    def measurements(self):
        return self._measurements

    def __getitem__(self, label_measurement):
        """
        Get item...
        """
        try:
            return self.measurements[label_measurement]
        except KeyError as error:
            raise KeyError(
                """
                {}: No such measurement.
                \t
                """.format(label_measurement, error))
        return None

    def __iter__(self):
        """..."""
        return self.measurements.__iter__()

    def __len__(self):
        """..."""
        return len(self.measurements)

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return OrderedDict([
            (
                label,
                measurement.assign(label=label).collect(
                    adapter, model, *args, **kwargs)
            ) for label, measurement in self.measurements.items()])
            

