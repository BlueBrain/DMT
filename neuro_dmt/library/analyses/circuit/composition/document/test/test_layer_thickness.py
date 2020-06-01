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
Test develop documents that analyze circuit composition.
"""

from dmt.tk.journal import Logger
from dmt.tk.field import Record
#from neuro_dmt.library.models.mock.circuit.model import MockCircuitModel
#from neuro_dmt.library.models.mock.circuit.adapter import MockCircuitAdapter
#from neuro_dmt.library.models.mock.circuit.test.mock_circuit_light\
    #import circuit_composition, circuit_connectivity
from .. import layer_thickness
from .import MockCircuitAdapter, MockCircuitModel

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def get_test_object():
    """..."""
    LOGGER.status(
        LOGGER.get_source_info(),
        """
        Get a document builder.
        """)
    document = layer_thickness.get()
    LOGGER.status(
        LOGGER.get_source_info(),
        """
        Build a circuit to work with.
        """)
    # circuit = MockCircuitModel(circuit_composition,
    #                            circuit_connectivity,
    #                            label="SSCxMockCircuit")

    circuit = MockCircuitModel()
    LOGGER.status(
        LOGGER.get_source_info(),
        """
        Get an adapter.
        """)
    adapter = MockCircuitAdapter()

    return Record(
        document=document,
        circuit=circuit,
        adapter=adapter)


def test_develop():
    """
    A documented analysis of layer thickness should:
    1.???
    """
    test_object = get_test_object()

    assert test_object.document


