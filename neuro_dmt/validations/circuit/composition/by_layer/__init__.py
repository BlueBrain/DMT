"""Utilities for circuit composition by layer."""
from abc import abstractmethod
from dmt.analysis.validation.test_case import SinglePhenomenonValidation
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import  document_fields
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.pandas import flatten
from dmt.vtk.utils.exceptions import ValueNotSetError
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.validations.circuit.composition \
    import SpatialCompositionValidation


@document_fields
class ByLayerCompositionValidation(SpatialCompositionValidation,
                                   SinglePhenomenonValidation):
    """Validation of a single circuit composition phenomenon.
    Validation is against reference data that provide experimental data
    as a function of layer. This base class may be used for validation
    composition of any brain region that is composed of layers.
    """
    plotter_type = BarPlotComparison

    def __init__(self, validation_data, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(measurement_label :: String,
        ~                              region_label :: String,
        ~                              data :: DataFrame["region", "mean", "std"])],
        ~                              citation :: Citation,
        ~                              what :: String)]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional
        report_file_name :: String #optional
        plot_customization :: Dict #optional
        """
        super(ByLayerCompositionValidation, self)\
            .__init__(validation_data, *args, **kwargs)

    @property
    def primary_dataset(self):
        """Override"""
        if isinstance(self._validation_data, Record):
            return self._validation_data.datasets[self._validation_data.primary]

        if isinstance(self._validation_data, dict):
            if len(self._validation_data) == 1:
                return list(self._validation_data.values())[0]
            if self._primary_dataset:
                return self._validation_data[self._primary_dataset]
            else:
                raise ValueNotSetError("_primary_dataset", self)

        if isinstance(self._validation_data, list):
            return self._validation_data[0]

        return self._validation_data

    @property
    def validation_data(self):
        """Override"""
        if self._validation_data is None:
            raise Exception("Test case {} does not use validation data"\
                            .format(self.__class__.__name__))
        data = (self._validation_data.datasets
                if isinstance(self._validation_data, Record) else
                self._validation_data)
        
        if not isinstance(data, dict):
            return data

        assert(isinstance(data, dict))
        if len(data) == 1:
            return list(data.values())[0]

        dataset_names = [k for k in data.keys()]
                           
        return flatten({n: data[n].data for n in dataset_names},
                       names=["dataset"])[["mean", "std"]]

    @property
    def validation_datasets(self):
        """Return validation data as a dict."""
        data = (self._validation_data.data
                if isinstance(self._validation_data, Record) else
                self._validation_data)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {d.label: d for d in data}
        return {data.label: data}
        
    def _set_measurement_parameters(self, circuit_model):
        """..."""

        def __parameter_filled(p, dataframe):
            """set parameter p for a single dataframe"""
            return p.filled(dataframe)

        data = (self._validation_data.data
                if isinstance(self._validation_data, Record) else
                self._validation_data)
        if isinstance(data, dict):
            self._validation_data = {k: }
        if isinstance(data, list):
            return {d.label: d for d in data}
        return {data.label: data}
        

    def data_description(self):
        """Describe the experimental data used for validation."""
        return self.primary_dataset.what
     
    def get_label(self, circuit_model):
        """Get a label for the circuit model. Will be useful in reporting."""
        return self.adapter.get_label(circuit_model)

    def get_report(self, model_measurement):
        """Create a report."""
        plot_dir, plot_name = self.plot(model_measurement,
                                        output_dir_path = self.output_dir_path,
                                        file_name = 'report.png')
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            validated_phenomenon = self.validated_phenomenon,
            validation_image_dir = ".", #keep image dir relative
            validation_image_name = plot_name,
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_datasets,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval
        )


from neuro_dmt.validations.circuit.composition.by_layer.cell_density \
    import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.cell_ratio \
    import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.inhibitory_synapse_density \
    import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.synapse_density \
    import SynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.soma_volume_fraction \
    import SomaVolumeFractionValidation
