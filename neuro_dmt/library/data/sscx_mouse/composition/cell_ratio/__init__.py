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


class LayerInhibitoryFractionMeasurement(SampleMeasurement):
    """
    Measurement of the fraction of inhibitory cells.
    """
    phenomenon = Phenomenon(
        "Inhibitory Fraction",
        description="Fraction of cells that are inhibitory",
        group="Composition")
    parameters = OrderedDict(
        layer="Layer where the inhibitory fraction was measured.")


class RegionInhibitoryFractionMeasurement(SampleMeasurement):
    """
    Measurement of the fraction of inhibitory cells.
    """
    phenomenon = Phenomenon(
        "Inhibitory Fraction",
        description="Fraction of cells that are inhibitory",
        group="Composition")
    parameters = OrderedDict(
        region="Region where the inhibitory fraction was measured.")


class ByRegionLayerInhibitoryFractionMeasurement(SampleMeasurement):
    """
    Measurement of the fraction of inhibitory cells.
    """
    phenomenon = Phenomenon(
        "Inhibitory Fraction",
        description="Fraction of cells that are inhibitory",
        group="Composition")
    parameters = OrderedDict(
        layer="Layer where the cells were counted",
        region="Name of the brain region where the inhibitory fraction was measured.")
    
def inhibitory_fraction_defelipe(subregions=["SSCx"], path_dmt=None):
    """
    Mouse SSCx layer inhibitory fraction data provided by the DeFelipe lab.
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
        "sscx_mouse", "composition"
    )
    defelipe_2018_inhibitory_fraction_dataset =  datasets.load(
        path_mouse_data.joinpath("cell_ratio"),
        "LeFort2009"
    )
    count_all = np.array(
        defelipe_2018_inhibitory_fraction_dataset["count_all"]
    )
    count_inh = np.array(
        defelipe_2018_inhibitory_fraction_dataset["count_inh"]
    )
    data_original = pd.DataFrame({
        ("inhibitory_fraction", "mean"): count_inh / count_all,
        ("inhibitory_fraction", "std"):  1./np.sqrt(count_all)}
    ).assign(
        layer=["L{}".format(l) for l in range(1, 7)]
    ).set_index("layer")

    if not subregions:
        data = data_original
        MeasurementType = Summary(LayerInhibitoryFractionMeasurement)
    else:
        data = pd.concat(
            [data_original for _ in subregions],
            keys=subregions,
            names=["region"]
        )
        MeasurementType = Summary(ByRegionLayerInhibitoryFractionMeasurement)

    return MeasurementType(
        label=defelipe_2018_inhibitory_fraction_dataset["short_name"],
        object_of_observation="Somatosensory cortexes of a population of mice",
        procedure=defelipe_2018_inhibitory_fraction_dataset["what"],
        provenance="DeFelipe Lab, 2018",
        citation=defelipe_2018_inhibitory_fraction_dataset["citation"],
        uri=defelipe_2018_inhibitory_fraction_dataset["uri"],
        data=data.reset_index()
    )
