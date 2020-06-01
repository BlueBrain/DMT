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
from pathlib import Path
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Record
from neuro_dmt import terminology

#from neuro_dmt.library.models.mock.circuit.model import MockCircuitModel
#from neuro_dmt.library.models.mock.circuit.adapter import MockCircuitAdapter
#from neuro_dmt.library.models.mock.circuit.test.mock_circuit_light\
    #import circuit_composition, circuit_connectivity

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ =[X, Y,Z]
LAYER = terminology.bluebrain.cell.layer
REGION = terminology.bluebrain.cell.region


class MockCircuitModel:
    def __init__(self, *args, **kwargs):
        pass

    layers = ["L1", "L2", "L3", "L4", "L5", "L6"]
    layer_type = "Cortical"
    brain_region = "SSCxO1"
    subregions = ["mc{}_Column".format(c) for c in range(0, 7)]


class MockCircuitAdapter:
    def __init__(self, *args, **kwargs):
        pass

    def get_label(self, model):
        return "MockModel"

    def get_brain_region(self, model):
        return model.brain_region
    def get_sub_regions(self, model):
        return model.subregions

    def get_layer_type(self, model):
        return model.layer_type

    def get_layers(self, model):
        return model.layers

    def get_provenance(self, model, **kwargs):
        return dict(
            animal="Mockque",
            age="Mockinteen",
            brain_region="Mock's Area",
            date_release="MockMockMock",
            label="MockModel",
            uri="http://mock/mock/mock",
            authors=["Mock Mockonly"])

    def get_namespace(self, model):
        return {
            "layer-values": self.get_layers(model),
            "layer-type": self.get_layer_type(model),
            "region": self.get_brain_region(model),
            "sub-regions": self.get_sub_regions(model),
            "animal": "Mouse"}

    def get_layer_thickness_values(self,
            circuit_model,
            sample_size=100,
            **spatial_query):
        """
        A mock value to develop with.
        """
        layers = self.get_layers(circuit_model)
        n_layers = len(layers)
        def _thickness(position):
            return pd.Series(
                np.random.normal(2000., 50., n_layers),
                index=layers)
        positions = pd.DataFrame(
            np.random.uniform(size=(sample_size, 3)),
            columns=XYZ
        )
        return positions.apply(_thickness, axis=1)



TESTOBJ = None

def get_test_object(chapter):
    """..."""
    global TESTOBJ

    if not TESTOBJ:
        LOGGER.status(
            LOGGER.get_source_info(),
            """
            Get a document builder.
            """)
        document = chapter.get()
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
        
        TESTOBJ = Record(document=document,
                         circuit_model=circuit,
                         adapter=adapter)

    return TESTOBJ

def get_path_save():
    folder =  Path.cwd().joinpath("folder_test")
    folder.mkdir(parents=False, exist_ok=True)
    return folder
