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
Adapter for the mock BBP circuit.
"""

import numpy
import pandas
from dmt.model import interface, adapter
from dmt.tk.field import WithFields, Field, lazyproperty
from .model import MockCircuitModel
from neuro_dmt import terminology


@adapter.adapts(MockCircuitModel)
class MockCircuitAdapter(WithFields):
    """
    A mock adapter for a mock circuit.

    This adapter is not to be used for the `MockCircuit` defined in
    `neuro_dmt.models.bluebrain.mock.circuit`. `MockCircuit` is intended
    to behave like actual BBP circuits, as closely as posible.

    `MockCircuitAdapter`'s logic is independent and implemented to quick
    development of the analysis --- plotting, report generation etc.
    """

    def get_namespace(self, circuit_model):
        """
        A dict describing the circuit.
        """
        return {
            "cortical-thickness-estimated-range": "2-3mm",
            "animal": "Mockaque"}

    def get_label(self,
            mock_circuit_model):
        """
        Label for a mock circuit model.
        """
        return "mock_circuit"

    def get_method_description(self,
            name_measurement,
            sampling_methodology=terminology.sampling_methodology.random,
            **kwargs):
        """
        Describe methods.
        """
        return "Mock Mock Mock"

    def get_cell_density(self,
            mock_circuit_model,
            *args, **kwargs):
        """
        Mock cell density.
        """
        try:
            layer = kwargs["layer"]
            cell_density_layer = {
                1: 10000.0,
                2: 140000.0,
                3: 100000.0,
                4: 150000.0,
                5: 100000.0,
                6: 120000.0}
            return numpy.random.normal(
                cell_density_layer[layer],
                10. * numpy.sqrt(cell_density_layer[layer]))
        except AttributeError:
            return numpy.random.uniform(0., 100000.)

        raise Exception(
            "Code excecution should not reach here.")

    def get_inhibitory_cell_fraction(self,
                mock_circuit_model,
                *args, **kwargs):
        """
        Mock inhibitory cell fraction.
        """
        return numpy.random.unform(0., 1.)
