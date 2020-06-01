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
from dmt.model.interface import interfacemethod
from pathlib import Path
from dmt.tk.plotting import Bars, MultiPlot
from dmt.analysis.document.builder import DocumentBuilder

def get():
    """
    Build a document that analyzes layer thickness.
    """

    document = DocumentBuilder("Layer Thickness")
    @document.introduction
    def _():
        """
        Total thickness of cortical layers varies over the neocortex
        (\\model{cortical-thickness-estimated-range}) in the \\model{animal}.
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
        return Path.cwd().joinpath("resources/neocortical_scaffold.png")

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

    def layer_thickness(adapter, circuit_model, **parameters):
        wide = adapter.get_layer_thickness_values(circuit_model, **parameters)
        wide.columns.name = "layer"
        return pd.concat(
            [wide.iloc[i] for i in range(wide.shape[0])]
        ).rename(
            "thickness"
        )

    @document.methods.measurements
    def cortical_thickness(adapter, circuit_model, **parameters):
        """
        Measurement to be made on `circuit_model` for given `parameters`
        """
        raise NotImplementedError(
            """
            Do not worry about the adapter before  starting to implement.
            Assume it does not exist, and work your way through the logic
            by coding away.
            Once the code is written, all of it right here inside the body
            of this function, take another look at it and factor away the
            common adaptable code.
            """)
    @document.methods.measurements
    def relative_thickness(adapter, circuit_model, **parameters):
        """
        Measurement to be made on `adapter, circuit_model` for given
        `parameters`.
        """
        raise NotImplementedError(
            """
            Do not worry about the adapter before  starting to implement.
            Assume it does not exist, and work your way through the logic
            by coding away.
            Once the code is written, all of it right here inside the body
            of this function, take another look at it and factor away the
            common adaptable code.
            """)

    @document.results
    def _():
        """
        Results are presented in the figures.
        """
        pass

    @document.results.illustration
    def cortical_thickness():
        """
        Total thickness of cortical tissue for the regions modeled,
        plotted along experimental measurements.
        """
        return Bars(
            xvar="region", xlabel="Layer",
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


