"""
Datasets used / created at the Blue Brain Project for the rat.
"""

import os
from collections import OrderedDict
import numpy
import pandas
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.utils import datasets
from dmt.data.observation import\
    SampleMeasurement,\
    Summary
from neuro_dmt import data


class ByLayerCellDensityMeasurement(
        SampleMeasurement):
    """
    Measurement of cell density, by (cortical) layer.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        description="Count of cells per unit volume.",
        group="Composition")
    parameters = OrderedDict(
        layer="Cortical layer where to count the cells in.")


__path_cell_density_datasets =\
    os.path.join(
        data.LOCATION,
        "cortex/sscx/rat/composition",
        "cell_density")
__defelipe_2017_dataset =\
    datasets.load(
        __path_cell_density_datasets,
        "DeFelipe2017")

layers = ["L{}".format(l) for l in range(1,7)]
defelipe2017 =\
    ByLayerCellDensityMeasurement(
        label=__defelipe_2017_dataset["short_name"],
        object_of_observation="A population of 6 Wistar rats.",
        procedure=__defelipe_2017_dataset["what"],
        provenance="DeFelipe Lab, 2017",
        citation=__defelipe_2017_dataset["citation"],
        uri=__defelipe_2017_dataset["uri"],
        data=pandas.concat([
            pandas.DataFrame(
                dict(sample=rat,
                     layer=layers,
                     thickness=dataset["thicknesses"],
                     cell_density=dataset["densities"]))
            for rat, dataset in __defelipe_2017_dataset["circuits"].items()]))

__defelipe_2014_dataset =\
    datasets.load(
        __path_cell_density_datasets,
        "DeFelipe2014")
defelipe2014 =\
    ByLayerCellDensityMeasurement(
        label=__defelipe_2014_dataset["short_name"],
        object_of_observation="A population of 6 Wistar rats.",
        procedure=__defelipe_2014_dataset["what"],
        provenance="DeFelipe Lab, 2014",
        citation=__defelipe_2014_dataset["citation"],
        uri=__defelipe_2014_dataset["uri"],
        data=pandas.concat([
            pandas.DataFrame(
                dict(sample=rat,
                     layer=layers,
                     thickness=dataset["thicknesses"],
                     cell_density=dataset["densities"]))
            for rat, dataset in __defelipe_2014_dataset["circuits"].items()]))

__meyer2010_dataset =\
    datasets.load(
        __path_cell_density_datasets,
        "Meyer2010")
meyer2010 =\
    ByLayerCellDensityMeasurement.SummaryType()(
        label=__meyer2010_dataset["short_name"],
        object_of_observation="Rats of age P27",
        provenance="Look at the citation",
        citation=__meyer2010_dataset["citation"],
        uri=__meyer2010_dataset["uri"],
        data=pandas.DataFrame(
            [[1.e3 * density_mean, 1.e3 * density_std]
             for density_mean, density_std in zip(
                     __meyer2010_dataset["density_means"],
                     __meyer2010_dataset["density_stds"])],
            columns=pandas.MultiIndex.from_tuples([
                ("cell_density", "mean"),
                ("cell_density", "std")])
        ).assign(
            layer=layers))


class ByLayerInhibitoryCellFractionMeasurement(SampleMeasurement):
    """
    Measurement of inhibitory cell fraction, by cortical layer.
    """
    phenomenon = Phenomenon(
        "Inhibitory Cell Fraction",
        description = "Fraction of inhibitory cells.",
        group="Composition"
    )
    parameters = OrderedDict(
        layer="Cortical layer where the inhibitory cell fraction was measured"
    )


__path_inhibitory_cell_fraction_datasets =\
    os.path.join(
        data.LOCATION,
        "cortex/sscx/rat/composition",
        "cell_ratio")

__ghobril_2012_dataset =\
    datasets.load(
        __path_inhibitory_cell_fraction_datasets,
        "Ghobril2012")
__ghobril_count_inhibitory =\
    numpy.array(__ghobril_2012_dataset["count_inh"])
__ghobril_count_total =\
    numpy.array(__ghobril_2012_dataset["count_all"])
__ghobril_mean =\
    __ghobril_count_inhibitory / __ghobril_count_total
__ghobril_std =\
    __ghobril_mean * numpy.sqrt(
        1./__ghobril_count_inhibitory + 1./__ghobril_count_total)
ghobril2012 =\
    ByLayerInhibitoryCellFractionMeasurement.SummaryType()(
        label=__ghobril_2012_dataset["short_name"],
        object_of_observation="Multi-stain confocal images",
        procedure=__ghobril_2012_dataset["what"],
        provenance=__ghobril_2012_dataset["citation"],
        citation=__ghobril_2012_dataset["citation"],
        uri=__ghobril_2012_dataset["uri"],
        data=pandas.DataFrame({
            ("inhibitory_cell_fraction", "mean"): __ghobril_mean,
            ("inhibitory_cell_fraction", "std"): __ghobril_std,
        }).assign(
            layer=layers))


__lefort2009_dataset =\
    datasets.load(
        __path_inhibitory_cell_fraction_datasets,
        "Lefort2009")
lefort2009 =\
    ByLayerInhibitoryCellFractionMeasurement.SummaryType()(
        label=__lefort2009_dataset["short_name"],
        object_of_observation=__lefort2009_dataset["animal"],
        procedure="Not Available, read the paper",
        provenance="Read the paper",
        citation=__lefort2009_dataset["citation"],
        uri=__lefort2009_dataset["uri"],
        data=pandas.DataFrame({
            ("inhibitory_cell_fraction", "mean"): __lefort2009_dataset["ratio_means"],
            ("inhibitory_cell_fraction", "std"): __lefort2009_dataset["ratio_stds"]
        }).assign(
            layer=layers))

__beaulieu1992_dataset =\
    datasets.load(
        __path_inhibitory_cell_fraction_datasets,
        "Beaulieu1992")
beaulieu1992 =\
    ByLayerInhibitoryCellFractionMeasurement.SummaryType()(
        label=__beaulieu1992_dataset["short_name"],
        object_of_observation=__beaulieu1992_dataset["animal"],
        procedure="Not Available, read the paper",
        provenace="Read the paper",
        citation=__beaulieu1992_dataset["citation"],
        uri=__beaulieu1992_dataset["uri"],
        data=pandas.DataFrame({
            ("inhibitory_cell_fraction", "mean"): __beaulieu1992_dataset["ratio_means"],
            ("inhibitory_cell_fraction", "std"): __beaulieu1992_dataset["ratio_stds"]
        }).assign(
            layer=layers))
