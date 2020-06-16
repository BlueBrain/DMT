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
import os
from pathlib import Path
import random
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Record
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import CircuitProvenance
from neuro_dmt.library.models.sonata.circuit.model import SonataCircuitModel
from neuro_dmt.library.models.sonata.circuit.adapter import SonataCircuitAdapter

from neuro_dmt.library.models.mock.circuit.model import MockCircuitModel
from neuro_dmt.library.models.mock.circuit.adapter import MockCircuitAdapter
from neuro_dmt.library.models.mock.circuit.test.mock_circuit_light\
    import circuit_composition, circuit_connectivity

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ =[X, Y,Z]
LAYER = terminology.bluebrain.cell.layer
REGION = terminology.bluebrain.cell.region

CIRCUIT = os.environ.get("CIRCUIT", "MOCK")


class _MockCircuitModel:
    def __init__(self, *args, **kwargs):
        pass

    layers = ["L1", "L2", "L3", "L4", "L5", "L6"]
    layer_type = "Cortical"
    brain_region = "SSCxO1"
    #subregions = ["mc{}_Column".format(c) for c in range(0, 7)]
    subregions = ["SSCx"]
    xrange = (0., 1000.)
    yrange = (0., 2000.)
    zrange = (0., 1000.)
    inh_frac = {
        "L1": 1.,
        "L2": 105./648.,
        "L3": 118.78 / 1265.84,
        "L4": 139. / 1788.,
        "L5": 221. / 1317.,
        "L6": 132. / 1422.
    }
    mtypes = ["L1_IC", "L23_IC", "L23_PC", "L4_IC", "L4_PC",
              "L5_IC", "L5_PC", "L6_IC", "L6_PC"]

class _MockCircuitAdapter:
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

    def get_mtypes(self, model):
        return model.mtypes

    def get_cells(self, model, **kwargs):
        """..."""
        def _random_cell():
            layer = random.choice(self.get_layers(model))
            mtype = random.choice(model.mtypes)
            return {
                "layer": layer,
                "region": random.choice(self.get_sub_regions(model)),
                "mtype": mtype,
                "x": np.random.uniform(*model.xrange),
                "y": np.random.uniform(*model.yrange),
                "z": np.random.uniform(*model.zrange),
                "morph_class": "INT" if "IC" in mtype else "EXC"
            }
        return pd.DataFrame([
            _random_cell() for _ in range(100)
        ])

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

    def get_height(self, model, depth):
        return model.yrange[1] - depth


TESTOBJ = None

def get_test_object(chapter=None, **kwargs):
    """..."""
    global TESTOBJ

    if not TESTOBJ:
        LOGGER.status(
            LOGGER.get_source_info(),
            """
            Get a document builder.
            """)
        try:
            get_chapter = chapter.get
        except AttributeError:
            try:
                chapter = chapter.document
            except AttributeError:
                chapter = chapter.article
            document = chapter.get(sample_size=100, **kwargs)
        else:
            document = get_chapter(sample_size=100, **kwargs)
        LOGGER.status(
            LOGGER.get_source_info(),
            """
            Build a circuit to work with.
            """)
        if CIRCUIT == "MOCK":
     #       circuit = MockCircuitModel(circuit_composition,
     #                                  circuit_connectivity,
     #                                  label="SSCxMockCircuit")
     #       adapter = MockCircuitAdapter()
            circuit = _MockCircuitModel()
            adapter = _MockCircuitAdapter()
        else:
            LOGGER.status(
                LOGGER.get_source_info(),
                """
                Loading circuit and adapter assuming path to a circuit.
                \t {}
                """.format(CIRCUIT))
            circuit =\
                SonataCircuitModel(
                    path_circuit_data=CIRCUIT,
                    provenance=CircuitProvenance(
                        label="BlueBrainCircuitModel",
                        authors=["BBP Team"],
                        data_release="20200330",
                        uri=CIRCUIT,
                        animal="Mouse",
                        age="Not Available",
                        brain_region="SSCx"))
            adapter =\
                SonataCircuitAdapter(
                    model_has_subregions=False)

            
        TESTOBJ = Record(document=document,
                         circuit_model=circuit,
                         adapter=adapter)
    LOGGER.status(
        "test object: {}".format(TESTOBJ)
    )
    return TESTOBJ

def get_path_save():
    folder =  Path.cwd().joinpath("folder_test")
    folder.mkdir(parents=False, exist_ok=True)
    return folder
