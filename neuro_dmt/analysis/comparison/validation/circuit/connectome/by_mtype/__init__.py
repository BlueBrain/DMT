"""Validations of the circuit connectome, by mtype."""

import numpy as np
import pandas as pd
from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from neuro_dmt.analysis.comparison.circuit.connectome.by_mtype\
    import ByMtypeConnectomeComparison
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis\
    ,      PathwayConnectionCountAnalysis\
    ,      PathwayConnectionProbabilityAnalysis
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


class PairSynapseCountValidation(
        ByMtypeConnectomeValidation,
        PairSynapseCountAnalysis):
    pass


class PathwayConnectionCountValidation(
        ByMtypeConnectomeValidation,
        PathwayConnectionCountAnalysis):
    pass


class PathwayConnectionProbabilityValidation(
        ByMtypeConnectomeValidation,
        PathwayConnectionProbabilityAnalysis):
    pass

