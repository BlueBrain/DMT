# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published 
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
A test example to drive development of the various ways in which we can
develop circuit analyses.
"""


import numpy as np
import pandas as pd
from dmt.model.interface import interfacemethod, get_interface
from dmt.analysis import Adapted
from dmt.data.observation import measurement
from dmt.tk.journal import Logger
from dmt.tk.parameters import Parameters
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.plotting import Bars
from dmt.tk.reporting.section import Section
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import CircuitAnalysisReport
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis


LOGGER = Logger(client=__file__)

def adaptedmethod(m):
    """
    Define an analysis' method to be adapted...

    i.e insert `adapter, method,` before `method` arguments.
    """
    def effective(self, adapter, model, **kwargs):
        return m(self, model, **kwargs)

    return effective
        

class LayerThicknessAnalysis(Adapted, BrainCircuitAnalysis):
    """
    Analyze layer thickness of a brain-circuit
    """
    phenomenon = Phenomenon(
        "thickness",
        description="Thickness of a brain region",
        group="Composition")
    regions = Field(
        """
        Brain sub-regions to analyze layer thicknesses in.
        """)
    measurement_collection = Field(
        """
        A method to collect measurements for individual parameter set values.
        """,
        __default_value__=measurement.collection.series_type)
    plotter = Field(
        """
        A callable on plotting data that produces figures...
        """,
        __default_value__=Bars(
            xvar="layer",
            xlabel="Layer",
            yvar="thickness",
            ylabel="Thickness",
            gvar="region"))
    report = Field(
        """
        An callable that can create a report.
        """,
        __default_value__=CircuitAnalysisReport)

    @lazyfield
    def introduction(self):
        return Section.introduction("""
        The cortex consists of layers of cells. Here we analyze how
        layer thicknesses vary over a brain region.
        """)
    
    @lazyfield
    def methods(self):
        return Section.methods("""
        Thickness of layers were measured as the shortest top-bottom line 
        passing through each voxel in the circuit's physical space.
        """)
    
    @lazyfield
    def measurement_parameters(self):
        return lambda *args, **kwargs: [{"region": r} for r in self.regions]
    
    @interfacemethod
    def get_layer_thickness_values(self,
            circuit_model,
            relative=False,
            region=None,
            **kwargs):
        """
        Get a sample of values for layer thickness in a named region of the
        circuit.

        Arguments
        --------------
        relative : Boolean indicating return of relative layer thickness 
        region : name of the region where the layer thickness must be computed.

        Notes
        --------------
        For brain regions with arbitrary shape, their thickness can be hard to
        define. The exact definition is left to the implementation. What this
        analysis expects is a collection (`pandas.Series`) that may contain
        a sample of values for each layer in the named region.
        """

    @adaptedmethod
    def sample_measurement(self, circuit_model, **kwargs):
        """
        Measure a sample to use for analysis.

        Arguments
        -----------
        kwargs : Keyword arguments containing a circuit query,
        ~        and other specification...
        """
        wide =\
          self.get_layer_thickness_values(circuit_model, **kwargs)
        wide.columns.name =\
            "layer"
        return\
            pd.concat([wide.iloc[i] for i in range(wide.shape[0])])\
              .rename("thickness")



class MockCircuit:
    """..."""
    pass

class MockAdapter:
    """..."""
    def get_label(self, circuit_model):
        return "MockCircuit"

    def get_provenance(self, circuit_model, **kwargs):
        return dict(
            animal="mock",
            age="mock",
            brain_region="mock",
            data_release="mock",
            label="mock",
            uri="mock",
            authors=["mock"])

    def get_layer_thickness_values(self, *args, **kwargs):
        return pd.DataFrame(
            np.random.uniform(0., 1., size=(10000, 6)),
            columns=["L{}".format(l) for l in range(1, 7)])


def test_mock():
    """
    ...
    """
    circuit = MockCircuit()
    adapter = MockAdapter();
    analysis_layer_thickness = LayerThicknessAnalysis(adapter=adapter);
    layer_thickness = analysis_layer_thickness(circuit)

