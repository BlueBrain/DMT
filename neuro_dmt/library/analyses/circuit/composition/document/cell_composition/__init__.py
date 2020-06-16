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
Document cell composition of a circuit.
"""
import numpy as np
import pandas as pd
from dmt.model.interface import interfacemethod
from dmt.data.observation import measurement, SampleMeasurement, Summary
from pathlib import Path
from dmt.tk.journal import Logger
from dmt.tk.author import Author
from dmt.tk.plotting import Bars, MultiPlot, LinePlot
from dmt.tk.utils import datasets
from dmt.analysis.document.measurement import CompositeData, Measurement
from dmt.analysis.document.builder import LabReportBuilder
from neuro_dmt import terminology
from neuro_dmt.utils.geometry import Cuboid
from neuro_dmt.library.data.sscx_mouse.composition.cell_density import\
    cell_density_defelipe
from neuro_dmt.library.data.sscx_mouse.composition.cell_ratio import\
    inhibitory_fraction_defelipe

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ = [X, Y, Z]

LOGGER = Logger(client=__file__)


def get(sample_size=100):
    """
    Build a document that analyzes cell composition of a circuit.
    """

    document = LabReportBuilder("Cell Composition", author=Author.zero)

    @document.abstract
    def _():
        """
        Cell density and cell-type diversity in reconstructed brain region
        are analyzed and validated against experimental data.
        """
        pass

    @document.introduction
    def _():
        """
        Cell densities are an essential input to building a realistic
        brain-region circuit. Cell density varies widely across the cortex.
        Layer boundaries are determined experimentally by locating transitions
        in cell densities and soma-sizes. Accordingly, a reconstruction of
        a brain region should have the same cell densities in its various sub-regions
        as that observed experimentally, and reproduce the input values.


        Individual neurons show a lot of morphological and electro-physiological
        diversity. A brain reconstruction must also reproduce experimentally
        observed neuronal diversity across the modeled regions. In this report
        we analyze cell densities  and cell type diversity across the modeled
        brain regions:

        \\begin{itemize}
        \\item Overall cell density by layer
        \\item Fraction of inhibitory neurons by layer
        \\item Fractions for different cell {\\it mtype}s.
        \\end{itemize}
        """
        pass

    @document.methods
    def _():
        """
        We perform statistical tests in order to compare the {\\it in-silico}
        means against the {\\it in-experimentum} means.
        The null-hypothesis is that the {\\it in-silico} mean and the
        {\\it in-experimentum} mean are the same. The alternative hypothesis is
        that the two means are different.
        """
        pass

    @document.methods
    def statistical_testing():
        """
        The {\\it in-silico} value is assumed to be a realization of a 
        random variable from a normal distribution with the mean and standard 
        deviation estimated from biological data. This assumption results in 
        the test statistic: $\\frac{X - \\bar{x}}{\\bar{s}}$. The test statistic
        follows a normal distribution with zero mean and standard deviation 1.
        When a given dataset contains multiple data points, {\\it e.g.} cell density
        across layers, a pooled p-value is computed as
        $-2\\sum_{i=1} \\log p_i$ according to Fischer's method.
        """
        pass

    @interfacemethod
    def get_cells(adapter, circuit_model, region_of_interest):
        """
        Get cells from the circuit model that lie in a region of interest.

        The returned object should be a `pandas.DataFrame` that provides
        properties of cells, one cell in each row.
        """
        raise NotImplementedError

    def random_position(adapter, circuit_model, region=None, layer=None):
        """
        Get a random position in a given `(region, layer)`.
        """
        assert region or layer
        cells = adapter.get_cells(circuit_model, region=region, layer=layer)
        return cells.sample(n=1)[XYZ].iloc[0].to_numpy(np.float)

    @interfacemethod
    def get_height(adapter, circuit_model, depth):
        """
        Get height above pia for model of a columnar brain circuit.
        """
        raise NotImplementedError

    def sample_cells(adapter, circuit_model,
                     size_roi=50, region=None, layer=None, depth=None,
                     **kwargs):
        """
        Cells in a random region of interest in the location
        determined by region and layer or by region and (cortical) depth.
        """
        if layer is None and depth is None:
            raise TypeError(
                """
                sample_cells(...) called with neither a value for layer,
                nor a value for depth:
                This method requires one and only one of these two arguments.
                """)
        if layer is not None and depth is not None:
            raise TypeError(
                """
                sample_cells(...) called with values for both layer ({}),
                and depth ({}).
                This method requires one and only one of these two arguments.
                """.format(layer, depth))
        if layer is None:
            layer = 4
        position = random_position(adapter, circuit_model,
                                   region=region, layer=layer)

        if depth is not None:
            position[1] = adapter.get_height(circuit_model, depth)

        region_of_interest = Cuboid(position - size_roi/2, position + size_roi/2)
        return adapter.get_cells(circuit_model, region=region_of_interest)

    @interfacemethod
    def get_sub_regions(adapter, model):
        """
        The `adapter` should implement a method to get brain regions that were
        reconstructed in the given `model`. The modeled regions are the
        sub-regions of the larger modeled region.
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
        regions = adapter.get_sub_regions(model)
        layers = adapter.get_layers(model)
        return pd.DataFrame(
            [[r, l] for r in regions for l in layers],
            columns=["region", "layer"])

    @document.methods.reference_data
    def cell_density(path_dmt=None, n=20):
        """
        Experimental data for cell density used to validate the model.
        The data was provided by the DeFelipe Lab (2018).
        """
        summary_data = cell_density_defelipe(path_dmt=path_dmt)
        samples = summary_data.sample_measurement(n)
        samples.data = samples.data.set_index(["region", "layer"])
        return CompositeData({"InputConstraintDeFelipe2018": samples})

    def get_cell_density(adapter, circuit_model, size_roi=50., **query):
        """
        Get cell density for a given query.
        """
        cells = sample_cells(adapter, circuit_model,
                             size_roi=size_roi,
                             **query)
        return 1.e9 * cells.shape[0] / np.power(size_roi, 3)

    @document.methods.measurements
    def cell_density(adapter, circuit_model, *args, **kwargs):
        """
        To mimic an experimental measurement of cell density, cells were counted
        in random regions of interest (ROIs). For each set of parameters
        ({\\it i.e.} regions and layers in the model), 100 ROIs in the shape
        of cuboids of side 50 $\\mu m$ were sampled. Cell density was determined
        as the count of cells in each ROI divided by it's volume.
        """
        return Measurement(
            label="cell_density",
            parameters=regions_and_layers,
            method=get_cell_density,
            sample_size=sample_size
        ).collect(
            adapter, circuit_model, **kwargs
        )
    def mtypes_regions_and_layers(adapter, model, *args, **kwargs):
        """..."""
        regions = adapter.get_sub_regions(model)
        layers = adapter.get_layers(model)
        mtypes = adapter.get_mtypes(model)
        return pd.DataFrame(
            [[m, r, l] for m in mtypes for r in regions for l in layers],
            columns=["mtype", "region", "layer"]
        )
    @document.methods.measurements
    def cell_density_by_mtype(adapter, circuit_model, *args, **kwargs):
        """
        Cell densities of a given mtype was computed in the same way as
        overall cell density except that only the subset of cells with the given
        mtype were counted.
        """
        return Measurement(
            label="cell_density",
            parameters=mtypes_regions_and_layers,
            method=get_cell_density,
            sample_size=sample_size
        ).collect(
            adapter, circuit_model, **kwargs
        )
    @document.methods.reference_data
    def inhibitory_fraction(path_dmt=None, n=20):
        """
        Experimental data for inhibitory fraction used to validate the model.
        The data was provided by the DeFelipe Lab (2018).
        """
        summary_data = inhibitory_fraction_defelipe(path_dmt=path_dmt)
        samples = summary_data.sample_measurement(n)
        samples.data = samples.data.set_index(["region", "layer"])
        return CompositeData({"InputConstraintDeFelipe2018": samples})

    @document.methods.measurements
    def inhibitory_fraction(adapter, circuit_model, *args, **kwargs):
        """
        To mimic an experimental measurement of inhibitory fraction, cells were counted
        in random regions of interest (ROIs). For each set of parameters
        ({\\it i.e.} regions and layers in the model), 100 ROIs in the shape
        of cuboids of side 50 $\\mu m$ were sampled. Inhibitory fraction was
        measured as the number of inhibitory cells in each ROI divided by the
        number of total cells in that ROI.
        """
        def measurement_parameter_set(*args, size_roi=50, **query):
            region = query.get("region")
            layer = query.get("layer")
            depth = query.get("depth")
            cells = sample_cells(adapter, circuit_model,
                                 size_roi=size_roi,
                                 region=region,
                                 layer=layer,
                                 depth=depth,
                                 **kwargs)
            if cells.shape[0] == 0:
                return np.nan
            counts_morph_class = cells.groupby("morph_class").agg("size")
            try:
                n_inh = counts_morph_class.INT
            except AttributeError:
                return 0.
            return n_inh / cells.shape[0]

        return Measurement(
            label="inhibitory_fraction",
            parameters=regions_and_layers,
            method=measurement_parameter_set,
            sample_size=sample_size
        ).collect(
            adapter, circuit_model, **kwargs
        )
    @document.methods.measurements
    def mtype_fraction(adapter, circuit_model, *args, **kwargs):
        """
        Fraction of cells of a given mtype were computed over all the cells in
        a layer.
        """
        def measurement_parameter_set(*args, size_roi=50, **query):
            cells = adapter.get_cells(circuit_model, **query)
            mtype_counts = cells.mtype.value_counts()
            mtype_counts.index.name = "mtype"
            return mtype_counts/mtype_counts.sum()

        return Measurement(
            label="mtype_fraction",
            parameters=regions_and_layers,
            method=measurement_parameter_set,
            collection=measurement.collection.series_type,
            sample_size=sample_size
        ).collect(
            adapter, circuit_model, **kwargs
        )

    def regions_and_depths(adapter, circuit_model, *args,
                           n_bins_depth=20, **kwargs):
        """
        This works only for an O1 geometry.
        For atlas-based the atlas should provide the depths.
        """
        cells = adapter.get_cells(circuit_model)
        depth_max = cells.y.max()
        depth_min = cells.y.min()
        return pd.DataFrame([
            {"region": region, "depth": depth}
            for region in adapter.get_sub_regions(circuit_model)
            for depth in np.linspace(depth_min, depth_max, n_bins_depth)
        ])
    @document.methods.measurements
    def cell_density_by_depth(adapter, circuit_model, *args, **kwargs):
        """
        Cells were counted in random regions of interest (ROI).
        Several ROIs were sampled for each depth.
        Because only the center of an ROI was required to lie in a layer,
        it may overlap a neighboring layer. For such ROIs cell density
        measurement would be an overlap of those of the two neighboring layers
        that the ROI covers.
        """
        return Measurement(
            label="cell_density",
            parameters=regions_and_depths,
            method=get_cell_density,
            sample_size=sample_size
        ).collect(
            adapter, circuit_model, **kwargs
        )
    @document.results
    def _():
        """
        Results are presented as figures.
        """
        pass

    @document.results.illustration
    def cell_density():
        """
        Cell density by layer.
        """
        return MultiPlot(
            mvar="region",
            plotter=Bars(
                xvar="layer", xlabel="Layer",
                yvar="cell_density", ylabel="Cell Density",
                gvar="dataset"))

    @document.results.illustration
    def inhibitory_fraction():
        """
        Cell density by layer.
        """
        return MultiPlot(
            mvar="region",
            plotter=Bars(
                xvar="layer", xlabel="Layer",
                yvar="inhibitory_fraction", ylabel="Inhibitory Fraction",
                gvar="dataset"))

    @document.results.illustration
    def mtype_fraction():
        """
        Cell density by mtype and layer.
        """
        return MultiPlot(
            mvar="layer",
            plotter=Bars(
                xvar="mtype", xlabel="mtype",
                yvar="mtype_fraction", ylabel="fraction",
                gvar="region")
        )
    @document.results.illustration
    def cell_density_by_depth():
        """
        Cell density [$mm^3$] plotted against depth [$\\mu m$].
        """
        return LinePlot(xvar="depth", xlabel="Cortical Depth",
                        yvar="cell_density", ylabel="Cell Density",
                        gvar="region")

    return document.get()
