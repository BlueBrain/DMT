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
Test develop documented analyses.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
from dmt.tk.plotting import Bars, MultiPlot
from dmt.tk.plotting.figure import Figure
from dmt.tk.parameters import Parameters
from .. import *


class MockModel:
    layers = ["L1", "L2", "L3", "L4", "L5", "L6"]
    subregions = ["S1HL", "S1FL", "S1Sh", "S1Tr"]
    pass


class MockAdapter:
    """..."""
    def get_label(self, model):
        return "MockModel"

    def get_brain_regions(self, model):
        return model.subregions

    def get_layers(self, model):
        return ["L1", "L2", "L3", "L4", "L5", "L6"]

    def get_provenance(self, model, **kwargs):
        return dict(
            animal="mock",
            age="mock",
            brain_region="mock",
            data_release="mock",
            label="mock",
            uri="mock",
            authors=["mock"])

    def get_namespace(self, model):
        return {
            "layer_values": self.get_layers(model),
            "layer_type": "cortical",
            "brain_region": "somatosensory cortex",
            "sub_brain_regions": "S1HL, S1FL, S1Sh, and S1Tr",
            "animal": "Wistar Rat"}

def mock_cell_density(*args, **kwargs):
    """
    Create a mock cortical layer cell density
    """
    sample_size =\
        kwargs.get("sample_size", 20)
    label =\
        kwargs.get("label", None)
    mean_cell_density =\
        kwargs.get("mean_cell_density", [1., 3., 2., 4., 2., 3.])
    std_cell_density =\
        kwargs.get("std_cell_density", 6 * [0.1])

    data =  pd.concat([
        pd.DataFrame({
            "layer": "L{}".format(layer + 1),
            "cell_density": np.random.normal(
                mean_cell_density[layer],
                std_cell_density[layer],
                sample_size)})
        for layer in range(6)])
    if label:
        return data.assign(sample=label)[["sample", "layer", "cell_density"]]
    return data

def mock_thickness(*args, **kwargs):
    """
    Create a mock cortical layer cell density
    """
    sample_size =\
        kwargs.get("sample_size", 20)
    label =\
        kwargs.get("label", None)
    mean_thickness =\
        kwargs.get("mean_thickness", [122.3, 113.5, 302.9, 176.4, 477.9, 647.3])
    std_thickness =\
        kwargs.get("std_thickness", 6 * [10.])

    data =  pd.concat([
        pd.DataFrame({
            "layer": "L{}".format(layer + 1),
            "thickness": np.random.normal(
                mean_thickness[layer],
                std_thickness[layer],
                sample_size)})
        for layer in range(6)])
    if label:
        return data.assign(sample=label)[["sample", "layer", "thickness"]]
    return data

def mock_inh_fraction(*args, **kwargs):
    """
    Create a mock cortical layer cell density
    """
    sample_size =\
        kwargs.get("sample_size", 20)
    mean_inh_fraction =\
        kwargs.get("mean_inh_fraction", [0., 0.1, 0.2, 0.1, 0.1, 0.3])
    std_inh_fraction =\
        kwargs.get("std_inh_fraction", 6 * [0.01])

    return pd.concat([
        pd.DataFrame({
            "layer": "L{}".format(layer + 1),
            "inhibitory_fraction": np.random.normal(
                mean_inh_fraction[layer],
                std_inh_fraction[layer],
                sample_size)})
        for layer in range(6)])

def mock_bars(phenomenon, *args, **kwargs):
    """
    A bars plotter.
    """
    bars = Bars(
        xvar="layer",
        xlabel="Layer",
        yvar=phenomenon,
        ylabel=' '.join(w.capitalize() for w in phenomenon.split()))
    if phenomenon == "cell_density":
        return bars(mock_cell_density(*args, **kwargs))
    elif phenomenon == "inhibitory_fraction":
        return barse(mock_inh_fraction(*args, **kwargs))
    return None

mock_cell_density_values =\
    pd.concat([
        mock_cell_density().assign(region=region)
        for region in MockModel.subregions
    ]).set_index(["region", "layer"])

def cell_density(adapter, model, **query):
    """..."""
    layer = query["layer"]
    region = query["region"]
    return mock_cell_density_values.loc[(region, layer)]\
                                   .sample(n=1)\
                                   .iloc[0]\
                                   .cell_density

mock_inh_fraction_values =\
    pd.concat([
        mock_inh_fraction().assign(region=region)
        for region in MockModel.subregions
    ]).set_index(["region", "layer"])

def inhibitory_fraction(adapter, model, **query):
    """..."""
    layer = query["layer"]
    region = query["region"]
    return mock_inh_fraction_values.loc[(region, layer)]\
                                   .sample(n=1)\
                                   .iloc[0]\
                                   .inhibitory_fraction

def regions_and_layers(adapter, model):
    regions = adapter.get_brain_regions(model)
    layers = adapter.get_layers(model)
    return pd.DataFrame(
        [[r, l] for r in regions for l in layers],
        columns=["region", "layer"])


def get_path_save():
    path_save = Path(os.getcwd()).joinpath("folder_test")
    path_save.mkdir(parents=False, exist_ok=True)
    return path_save

def mock_reference_data_cell_density():
    """
    Mock some reference data for cell density.
    """

    def _get(sample):
        """
        data for a single sample individual
        """
        return mock_cell_density(
            sample_size=1, label=sample
        ).merge(
            mock_thickness(sample_size=1, label=sample),
            on=["sample", "layer"]
        )
    data =\
        pd.concat([
            mock_cell_density(sample_size=5).assign(region=region)
            for region in MockModel.subregions])\
          .set_index(["region", "layer"])
              
    return Record(
        label="MockData",
        object_of_observation="A population of mock animals",
        procedure="Random generation",
        citation="This code, right here",
        uri=__file__,
        data=data)
        

def mock_reference_data_inhibitory_fraction():
    """
    Mock some reference data for cell density.
    """

    def _get(sample):
        """
        data for a single sample individual
        """
        return mock_inh_fraction(
            sample_size=1, label=sample
        ).merge(
            mock_thickness(sample_size=1, label=sample),
            on=["sample", "layer"]
        )

    data =\
        pd.concat([
            mock_inh_fraction(sample_size=5).assign(region=region)
            for region in MockModel.subregions])\
          .set_index(["region", "layer"])
    return Record(
        label="MockData",
        object_of_observation="A population of mock animals",
        procedure="Random generation",
        citation="This code, right here",
        uri=__file__,
        data=data)

