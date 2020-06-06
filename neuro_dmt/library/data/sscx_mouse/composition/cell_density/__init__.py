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


class LayerCellDensityMeasurement(SampleMeasurement):
    """
    Measurement of layer cell densities.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        description="Counts of cells per unit volume",
        group="Composition")
    parameters = OrderedDict(
        layer="Layer where the cells density was measured.")


class RegionCellDensityMeasurement(SampleMeasurement):
    """
    Measurement of cell density in a brain region.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        description="Counts of cells per unit volume",
        group="Composition")
    parameters = OrderedDict(
        region="Region where the cells density was measured.")


class ByRegionLayerCellDensityMeasurement(SampleMeasurement):
    """
    Measurement of layer cell densities, for regions in a brain.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        description="Counts of cells per unit volume",
        group="Composition")
    parameters = OrderedDict(
        layer="Layer where the cells were counted",
        region="Name of the brain region where cell density was measured.")
    
def cell_density_defelipe(subregions=["SSCx"], path_dmt=None):
    """
    Mouse SSCx layer cell density data provided by the DeFelipe lab.
    Cell densities were measured for only a single SSCx subregion (hind-limb).
    To validate a circuit modeling several sub-regions, we broadcast
    the available data to all of these sub-regions. It is only assumed that the
    queried sub-regions are those of the SSCx --- but the data provided by this
    method may be used for any sub-region values.

    Data will be loaded from files shipped with DMT.

    Arguments
    -----------------
    subregions :: SSCx subregions for which data is required
    path_dmt :: Where DMT is located on the file system.
    """
    path_dmt = Path(check_environment(DMTPATH, value=path_dmt))

    path_mouse_data = path_dmt.joinpath(
        "neuro_dmt", "library", "data",
        "sscx_mouse", "composition")
    defelipe_2018_cell_density_dataset =  datasets.load(
        path_mouse_data.joinpath("cell_density"),
        "Keller2018Feb14")

    data_original = pd.DataFrame(
        [[1.e3 * density_mean, 1.e3 * density_std]
         for density_mean, density_std in zip(
                 defelipe_2018_cell_density_dataset["density_means"],
                 defelipe_2018_cell_density_dataset["density_stds"])],
        columns=pd.MultiIndex.from_tuples([
            ("cell_density", "mean"),
            ("cell_density", "std")]
        )).assign(
            layer=["L{}".format(l) for l in range(1, 7)]
        ).set_index("layer")

    if not subregions:
        data = data_original
        MeasurementType = Summary(LayerCellDensityMeasurement)
    else:
        data = pd.concat(
            [data_original for _ in subregions],
            keys=subregions,
            names=["region"]
        )
        MeasurementType = Summary(ByRegionLayerCellDensityMeasurement)

    return MeasurementType(
        label=defelipe_2018_cell_density_dataset["short_name"],
        object_of_observation="Somatosensory cortexes of a population of mice",
        procedure=defelipe_2018_cell_density_dataset["what"],
        provenance="DeFelipe Lab, 2018",
        citation=defelipe_2018_cell_density_dataset["citation"],
        uri=defelipe_2018_cell_density_dataset["uri"],
        data=data.reset_index()
    )
