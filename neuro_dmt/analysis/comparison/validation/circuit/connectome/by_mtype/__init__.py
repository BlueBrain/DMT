"""Validations of the circuit connectome, by mtype."""

import copy
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from neuro_dmt.analysis.comparison.circuit.connectome.by_mtype\
    import ByMtypeConnectomeComparison
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis\
    ,      PairConnectionAnalysis\
    ,      PathwayConnectionProbabilityAnalysis\
    ,      CellBoutonDensityAnalysis
from neuro_dmt.analysis.comparison.validation.circuit\
    import CircuitPhenomenonValidationTestCase
from neuro_dmt.analysis.comparison.validation.report.single_phenomenon\
    import ValidationReport


@document_fields
class ByMtypeConnectomeValidation(
        CircuitPhenomenonValidationTestCase,
        ByMtypeConnectomeComparison):
    """Validation of a single circuit-connectome-phenomenon.
    Validation is against reference data that provide experimental data as
    function of mtype.
    """
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            ReportType=ValidationReport,
            *args, **kwargs)

    def get_measurement_parameters(self):
        """We want to validate the pathways represented in both the reference
        data and the circuit."""
        validation_data=\
            self.validation_data
        parameter_labels=\
            [p.label for p in self.measurement_parameters]
        data_index_dataframe=\
            pd.MultiIndex.to_frame(
                validation_data.index)
        data_index_tuples={
            tuple(row)
            for row in data_index_dataframe[parameter_labels].values}
        measurement_index_tuples={
            tuple(
                row[parameter.label]
                for parameter in self.measurement_parameters)
            for row in ParameterGroup(self.measurement_parameters).kwargs}
        common_parameter_values= (
            data_index_tuples.intersection(
                measurement_index_tuples))
        return[
            parameter.__class__(values=list(values))
            for parameter, values in zip(
                    self.measurement_parameters,
                    zip(*common_parameter_values))]

    def pvalue(self,
            model_measurement,
            *args, **kwargs):
        """Suppressed for now."""
        return np.nan

red_patch = mpatches.Patch(color='red', label='The red data')
plt.legend(handles=[red_patch])

def get_pathway_colors(measurement):
    """..."""
    measurement_index=\
        measurement\
        .data\
        .index\
        .to_frame()
    pathways=\
        zip(
            measurement_index["pre_mtype"],
            measurement_index["post_mtype"])
    colors=dict(
        EXC=dict(
            EXC="xkcd:lightgreen",
            INH="xkcd:green"),
        INH=dict(
            EXC="xkcd:red",
            INH="xkcd:magenta"))
    def __get_synapse_type(mtype):
        """..."""
        return\
            "EXC" if "PC" in mtype else "INH"
    def __get_pathway_color(pathway):
        """..."""
        pre_stype=\
            __get_synapse_type(
                pathway[0])
        post_stype=\
            __get_synapse_type(
                pathway[1])
        return\
            colors[pre_stype][post_stype]
    return{
        "color":[
            __get_pathway_color(pathway)
            for pathway in pathways],
        "legend":{
            "handles": [
                mpatches.Patch(
                    color=colors["EXC"]["EXC"],
                    label="EXC-->EXC"),
                mpatches.Patch(
                    color=colors["EXC"]["INH"],
                    label="EXC-->INH"),
                mpatches.Patch(
                    color=colors["INH"]["EXC"],
                    label="INH-->EXC"),
                mpatches.Patch(
                    color=colors["INH"]["INH"],
                    label="INH-->INH")]}}



class PairSynapseCountValidation(
        ByMtypeConnectomeValidation,
        PairSynapseCountAnalysis):

    def plot(self,
            model_measurement,
            compared_quantity="dataset",
            *args, **kwargs):
        """Override to customize color scheme."""
        kwargs.update(
            get_pathway_colors(
                model_measurement))
        return\
            super().plot(
                model_measurement,
                compared_quantity=compared_quantity,
                *args, **kwargs)


class PairConnectionValidation(
        ByMtypeConnectomeValidation,
        PairConnectionAnalysis):

    def plot(self,
            model_measurement,
            compared_quantity="dataset",
            with_full_axis_range=False,
            *args, **kwargs):
        """..."""
        kwargs.update(
            get_pathway_colors(
                model_measurement))
        if with_full_axis_range:
            kwargs["ymin"] = 0.
            kwargs["ymax"] = 1.
            kwargs["xmin"] = 0.
            kwargs["xmax"] = 1.
        return\
            super().plot(
                model_measurement,
                compared_quantity=compared_quantity,
                *args, **kwargs)


class PathwayConnectionProbabilityValidation(
        ByMtypeConnectomeValidation,
        PathwayConnectionProbabilityAnalysis):

    def plot(self,
            model_measurement,
            compared_quantity="dataset",
            with_full_axis_range=False,
            *args, **kwargs):
        """..."""
        kwargs.update(
            get_pathway_colors(
                model_measurement))
        if with_full_axis_range:
            kwargs["axis"]={
                "xmin": 0.,
                "xmax": 1.,
                "ymin": 0.,
                "ymax": 1.}
        return\
            super().plot(
                model_measurement,
                compared_quantity=compared_quantity,
                *args, **kwargs)


class CellBoutonDensityValidation(
        ByMtypeConnectomeValidation,
        CellBoutonDensityAnalysis):
    """Validate cell bouton densities."""

    def plot(self,
            model_measurement,
            compared_quantity="dataset",
            *args, **kwargs):
        """Override to customize color scheme."""
        mtypes=\
            model_measurement\
            .data\
            .index\
            .to_frame()[
                "mtype"]\
            .values
        kwargs.update({
            "color":[
            "green" if "PC" in mtype else "red"
            for mtype in mtypes]})
        return\
            super().plot(
                model_measurement,
                compared_quantity=compared_quantity,
                *args, **kwargs)
