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
import pandas as pd
from dmt.model.interface import interfacemethod
from dmt.data.observation import measurement, SampleMeasurement, Summary
from pathlib import Path
from dmt.tk.author import Author
from dmt.tk.plotting import Bars, MultiPlot
from dmt.tk.utils import datasets
from dmt.analysis.document.measurement import CompositeData
from dmt.analysis.document.builder import LabReportBuilder
from neuro_dmt.library.data.sscx_mouse.composition.layer_thickness import\
    cortical_thickness_defelipe,\
    relative_thickness_defelipe

def get(sample_size=100):
    """
    Build a document that analyzes layer thickness.
    """

    document = LabReportBuilder("Layer Thickness", author=Author.zero)

    @document.abstract
    def _():
        """
        Total cortical, and relative layer thicknesses are analyzed.
        """

    @document.introduction
    def _():
        """
        Total thickness of cortical layers varies over the neocortex
        in the \\model{animal}.
        Furthermore relative thickness of individual layers
        (i.e. layer thickness divided  by thickness of all the layers together)
        also varies. 

        In this chapter we analyze how layer thicknesses,
        both total and relative, vary  across regions, and validate
        the layer thickness of a reconstruction against experimental data.
        """
        pass

    @document.introduction.illustration
    def neocortical_scaffold():
        """
        The neocortex is a 2-3 mm thick sheet of tissue on the surface of the brain. The figure above shows a digitally reconstructed neocortical column.
        """
        return {
            "Top": Path.cwd().joinpath("resources/O1TopView.png"),
            "Side": Path.cwd().joinpath("resources/neocortical_scaffold.png")}

    @document.introduction.illustration
    def experimental_layers():
        """
        A slide showing experimentally observed layers in the mouse SSCx.
        The experimentalists marked 7 layers, splitting layer 5 into two. In the model,
        we have used the standard 6 cortical layers.
        """
        return {
            "_": Path.cwd().joinpath("resources/mouse_layers_experimental.png")}

    @document.methods
    def _():
        """
        Layer thickness can be very to not just measure, but even hard to define
        in the volume of a real brain.
        """
        pass

    @interfacemethod
    def get_layer_thickness_values(
            adapter,
            circuit_model,
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
        raise NotImplementedError

    @document.methods.reference_data
    def cortical_thickness(path_dmt=None, n=20):
        """
        Experimental data for cortical thickness used to validate the model.
        The data was provided by the DeFelipe lab (2018).
        """
        summary_data =\
            cortical_thickness_defelipe(path_dmt=path_dmt)
        samples =\
            summary_data.sample_measurement(n)
        samples.data =\
            samples.data\
                   .set_index("region")
        return CompositeData({
            "InputConstraintDeFelipe2018": samples})

    @document.methods.reference_data
    def relative_thickness(path_dmt=None, n=20):
        """
        Experimental data for relative thickness used to validate the model.
        The data was provided by the DeFelipe lab (2018).
        """
        summary_data =\
            relative_thickness_defelipe(path_dmt=path_dmt)
        samples =\
            summary_data.sample_measurement(n)
        samples.data =\
            samples.data\
                   .set_index(["region", "layer"])\
                   .rename(columns={"thickness": "relative_thickness"})
        return CompositeData({
            "InputConstraintDeFelipe2018": samples
        })

    @interfacemethod
    def get_sub_regions(adapter, model):
        """
        The `adapter` should implement a method to get brain regions that were
        reconstructed in the given `model`. The modeled regions are the
        sub-regions of the larger modeled region.
        """
        raise NotImplementedError
 
    @document.methods.measurements
    def layer_thicknesses(adapter, circuit_model, *args, **kwargs):
        """
        For each position in a sample, thicknesses of the layers were measured
        along an the local orientation of the cortical column.
        """
        values =  pd.concat([
            adapter.get_layer_thickness_values(
                circuit_model, region=region, **kwargs
            ).assign(region=region)
            for region in adapter.get_sub_regions(circuit_model)
        ]).set_index("region")
        values.columns.name = "layer"
        return values

    @document.methods.measurements
    def cortical_thickness(adapter, circuit_model, *args, **kwargs):
        """
        Measured layer thicknesses were summed at each sampled position
        to provide total cortical thickness.
        """
        return pd.DataFrame({
            "cortical_thickness": layer_thicknesses(
                adapter, circuit_model, *args, **kwargs
            ).sum(axis=1)})

    @document.methods.measurements
    def relative_thickness(adapter, circuit_model, *args, **kwargs):
        """
        Measured layer thicknesses at each sampled position were divided by
        the total cortical thickness at that position.
        """
        def _long(region, wide):
            return pd.concat([
                wide.iloc[i].rename(
                    "relative_thickness"
                ).reset_index().assign(
                    region=region
                ).set_index(
                    ["region", "layer"]
                ) for i in range(wide.shape[0])
            ])
        thicknesses = layer_thicknesses(
            adapter, circuit_model, *args, **kwargs
        ).apply(
            lambda row: row/row.sum(), axis=1
        )
        return pd.concat([
            _long(region, wide)
            for region, wide in thicknesses.groupby("region")])

    @document.results
    def _():
        """
        Results are presented in the figures.
        """
        pass

    def get_summary(samples):
        """..."""
        return 

    @document.results.tables
    def cortical_thickness(samples):
        """
        Summary statistics for cortical thickness measured in the model.
        """
        return samples.groupby("region")\
                      .agg(["mean", "std"])\
                      .cortical_thickness

    @document.results.tables
    def relative_thickness(samples):
        """
        Summary statistics for relative thickness measured in the model.
        """
        return samples.groupby(["region", "layer"])\
                      .agg(["mean", "std"])\
                      .relative_thickness

    @document.results.illustration
    def cortical_thickness():
        """
        Total thickness of cortical tissue for the regions modeled,
        plotted along experimental measurements.
        """
        return Bars(
            xvar="region", xlabel="Region",
            yvar="cortical_thickness", ylabel="Cortical Thickness",
            gvar="dataset")

    @document.results.illustration
    def relative_thickness():
        """
        Thickness of cortical layers relative to total cortical thickness,
        plotted along experimental measurements.
        """
        return MultiPlot(
            mvar="region",
            plotter=Bars(
                xvar="layer", xlabel="Layer",
                yvar="relative_thickness", ylabel="Relative Thickness",
                gvar="dataset"))

    return document.get()
