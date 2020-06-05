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
Wrap data with meta-data.
"""

import os
from pathlib import Path
from collections import OrderedDict
import numpy as np
import pandas as pd
from dmt.data.observation import SampleMeasurement, Summary
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.utils import datasets
from ..import check_environment, DMTPATH

class LayerThicknessMeasurement(SampleMeasurement):
    """
    Measurement of layer thicknesses.
    """
    phenomenon = Phenomenon(
        "thickness",
        description="Thickness of layers",
        group="Composition")
    parameters = OrderedDict(
        layer="Labels for layers where thickness was measured.")


class CorticalThicknessMeasurement(SampleMeasurement):
    """
    Measurement of total thickness of cortical layers.
    """
    phenomenon = Phenomenon(
        "cortical_thickness",
        description="Total cortical thickness.",
        group="Composition")
    parameters = OrderedDict(
        region="Labels for the (sub-)brain regions where layer thickness was measured.")


class ByRegionLayerThicknessMeasurement(SampleMeasurement):
    """
    Measurement of layer thicknesses.
    """
    phenomenon = Phenomenon(
        "thickness",
        description="Thickness of layers",
        group="Composition")
    parameters = OrderedDict(
        layer="Labels for layers where thickness was measured.",
        region="Labels for the (sub-)brain regions where layer thickness was measured.")


class ByRegionRelativeLayerThicknessMeasurement(SampleMeasurement):
    """
    Measurement of layer thicknesses divided by total cortical thickness.
    """
    phenomenon = Phenomenon(
        "relative_thickness",
        description="Thickness of layers",
        group="Composition")
    parameters = OrderedDict(
        layer="Labels for layers where thickness was measured.",
        region="Labels for the (sub-)brain regions where layer thickness was measured.")


def thickness_defelipe(subregions=["SSCx"], path_dmt=None):
    """
    Mouse SSCx layer-thickness data provided by the DeFelipe lab.
    Cortical thickness was measured for only a single SSCx subregion (hind-limb).
    To validate a circuit modeling several sub-regions, we broadcast the
    available data to all of these sub-regions.

    Data will be loaded from files shipped with DMT.

    Arguments
    ------------------
    subregions :: SSCx subregions for which data is required.
    path_dmt :: Where DMT is located on the file system
    """
    path_dmt = Path(check_environment(DMTPATH, value=path_dmt))
            
    path_mouse_data = path_dmt.joinpath(
        "neuro_dmt", "library", "data",
        "sscx_mouse", "composition")
    defelipe_2018_thickness_dataset =\
        datasets.load(
            path_mouse_data.joinpath("layer_thickness"),
            "DeFelipe20180212")

    data_original = pd.DataFrame(
        [[density_mean, density_std]
         for density_mean, density_std in zip(
                 defelipe_2018_thickness_dataset["means"],
                 defelipe_2018_thickness_dataset["errors"])],
        columns=pd.MultiIndex.from_tuples([
            ("thickness", "mean"),
            ("thickness", "std")])
    ).assign(
        layer=["L{}".format(l) for l in range(1, 7)]
    ).set_index("layer")

    if not subregions:
        data = data_original
        MeasurementType = Summary(LayerThicknessMeasurement)
    else:
        data = pd.concat(
            [data_original for _ in subregions],
            keys=subregions,
            names=["region"]
        )
        MeasurementType = Summary(ByRegionLayerThicknessMeasurement)
    return MeasurementType(
        label=defelipe_2018_thickness_dataset["short_name"],
        object_of_observation="Somatosensory cortexes of a population of mice.",
        procedure=defelipe_2018_thickness_dataset["what"],
        citation=defelipe_2018_thickness_dataset["citation"],
        uri=defelipe_2018_thickness_dataset["uri"],
        data=data.reset_index()
    )

def cortical_thickness_defelipe(subregions=["SSCx"], path_dmt=None):
    """
    Cortical thickness was measured for only a single SSCx subregion (hind-limb).
    To validate a circuit modeling several sub-regions, we broadcast the
    available data to all of these sub-regions.
    """
    thickness = thickness_defelipe(subregions=None, path_dmt=path_dmt)
    mean_total = thickness.data.thickness["mean"].sum()
    std_total = np.sqrt((thickness.data.thickness["std"] ** 2).sum())

    def _cortical_thickness(region=None):
        data = pd.DataFrame(
            [[mean_total, std_total]],
            columns=pd.MultiIndex.from_tuples([("cortical_thickness", "mean"),
                                               ("cortical_thickness", "std")])
        )
        if not region:
            return data
        return data.assign(region=region)

    def _with(data):
        return Summary(CorticalThicknessMeasurement)(
            label=thickness.label,
            object_of_observation=thickness.object_of_observation,
            procedure=thickness.procedure,
            citation=thickness.citation,
            uri=thickness.uri,
            data=data)

    if not subregions:
        return _with(
            _cortical_thickness())
    return _with(
        pd.concat([_cortical_thickness(region) for region in subregions]))

def relative_thickness_defelipe(subregions=["SSCx"], path_dmt=None):
    """
    Thickness of a layer, divided by total cortical thickness.

    Cortical thickness was measured for only a single SSCx subregion (hind-limb).
    To validate a circuit modeling several sub-regions, we broadcast the
    available data to all of these sub-regions.
    """
    thickness = thickness_defelipe(subregions=None, path_dmt=path_dmt)
    mean_total = thickness.data.thickness["mean"].sum()

    if not subregions:
        data =\
            thickness.data.set_index(
                "layer"
            )/ mean_total
        MeasurementType =\
            Summary(LayerThicknessMeasurement)
    else:
        data =\
            thickness_defelipe(
                subregions, path_dmt
            ).data.set_index(
                ["region", "layer"]
            ) / mean_total
        MeasurementType =\
            Summary(ByRegionLayerThicknessMeasurement)
    return MeasurementType(
        label=thickness.label,
        object_of_observation=thickness.object_of_observation,
        procedure=thickness.procedure,
        citation=thickness.citation,
        uri=thickness.uri,
        data=data.reset_index())
