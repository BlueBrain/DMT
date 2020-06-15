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
Document layer thickness of a circuit.
"""
from collections import OrderedDict
from pathlib import Path
from dmt.tk.field import NA, Record
from dmt.tk.journal import Logger
from ...components import *
from ...builder import *
from ..import test_composition
from ..test_composition import *
from ..import *

document = DocumentBuilder("Layer Thickness",
                           author=Author.zero)
@document.abstract
def _():
    """
    We analyze the densities of cortical layers \\model{layer_values}
    """
    pass

@document.introduction
def _():
    """
    Cortical area such as the \model{brain_region} is composed of layers
    of cells with different cell densities.
    In this report we analyze circuit composition of cortical layers
    \\model{layer_values}, focusing on total cell density and the fraction
    of inhibitory neurons in each layer. In our model of the
    \\model{brain_region} we have reconstructed the sub-regions
    \\model{sub_brain_regions}.
    Experimental measurements for cell densities for these sub-regions
    were not available.
    Hence we have used the same cell densities presented in the figure for
    each of the these regions.
    """
    pass

@document.introduction.illustration
def neocortical_scaffold():
    """
    The neocortex is a 2-3 mm thick sheet of tissue on the surface
    of the brain.
    The figure above shows a digitally reconstructed neocortical column.
    """

    return Path.cwd().joinpath(
        "resources/neocortical_scaffold.png")

@document.introduction.tables
def experimental_cell_density():
    """
    Mock experimental cell density.
    """
    return CompositeData({
        "experimental_cell_density": "resources/experimental_cell_density.csv"})

@document.methods
def _():
    """
    Random cell densities were assigned to each pair of (sub-region, layer) for sub-regions \\model{sub_brain_regions} and layers \\model{layer_values}, for the purposes of mocking the behavior of a `methods` instance.
    """
    pass

@document.methods.reference_data
def cell_density():
    """
    Experimentally measured cell density data.
    """
    return CompositeData({
        "abcYYYY": mock_reference_data_cell_density(),
        "uvwXXXX": mock_reference_data_cell_density()})
@document.methods.reference_data
def inhibitory_fraction():
    """
    Experimentally measured fraction of inhibitory cells.
    """
    return CompositeData({
        "abcYYYY": mock_reference_data_inhibitory_fraction(),
        "uvwXXXX": mock_reference_data_inhibitory_fraction()})
@interfacemethod
def get_brain_regions(adapter, model):
    """
    The `adapter` should implement a method to get brain regions that were
    reconstructed in the given `model`
    """
    raise NotImplementedError

@interfacemethod
def get_layers(adapter, model):
    """
    The `adapter` should implement a method to names used for the layers
    of brain region that were reconstructed in the given `model`.
    """
    raise NotImplementedError

def regions_and_layers(adapter, model, *args, **kwargs):
    """..."""
    for region in adapter.get_brain_regions(model):
        for layer in adapter.get_layers(model):
            yield (region, layer)

@document.methods.measurements
def cell_density(adapter, model, *args, **kwargs):
    """
    Layer cell densities for regions \\model{sub_brain_regions}.
    """
    def get_one(region, layer):
        return\
            mock_cell_density_values.loc[(region, layer)]\
                                    .sample(n=1)\
                                    .iloc[0]\
                                    .cell_density
    sample_size = kwargs.get("sample_size", 20)
    return pd.concat([
        pd.DataFrame({
            "region": region,
            "layer":  layer,
            "cell_density": [get_one(region, layer) for _ in range(sample_size)]
        }) for region, layer in regions_and_layers(adapter, model)
    ]).set_index(
        ["region", "layer"]
    )
@document.methods.measurements
def inhibitory_fraction(adapter, model, *args, **kwargs):
    """
    Layer inhibitory cell fractions for regions \\model{sub_brain_regions}.
    """
    def get_one(region, layer):
        return\
            mock_inh_fraction_values.loc[(region, layer)]\
                                    .sample(n=1)\
                                    .iloc[0]\
                                    .inhibitory_fraction
    sample_size = kwargs.get("sample_size", 20)
    return pd.concat([
        pd.DataFrame({
            "region": region,
            "layer": layer,
            "cell_density": [get_one(region, layer) for _ in range(sample_size)]
        }) for region, layer in regions_and_layers(adapter, model)
    ]).set_index(
        ["region", "layer"]
    )
@document.results
def _():
    """
    Random cell densities were assigned to each pair of
    (sub-region, layer) for sub-regions \\model{sub_brain_regions}
    and layers \\model{layer_values}, for the purposes of mocking the
    behavior of a `methods` instance.
    """
    pass

@document.results.illustration
def cell_density(measurement, *args, **kwargs):
    """
    Mock cell density for a cortical circuit.
    """
    return MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density",
            gvar="dataset"
        )
    )(measurement)

@document.results.illustration
def inhibitory_fraction(measurement, *args, **kwargs):
    """
    Mock inhibitory fraction for a cortical circuit.
    """
    return MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction",
            gvar="dataset")
    )(measurement)
