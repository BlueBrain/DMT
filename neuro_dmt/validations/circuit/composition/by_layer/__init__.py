"""Utilities for circuit composition by layer."""
from abc import abstractmethod
import pandas as pd
from dmt.data.reference import MultiReferenceData
from dmt.vtk.utils.descriptor import Field
from dmt.analysis.validation.test_case import SinglePhenomenonValidation
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import  document_fields
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from dmt.vtk.utils.pandas import flatten
from dmt.vtk.utils.exceptions import ValueNotSetError
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import ValidationReport
from neuro_dmt.validations.circuit.composition import SpatialCompositionAnalysis
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.measurement.parameter import LayerIndex, CorticalLayer
    

@document_fields
class ByLayerCompositionValidation(SpatialCompositionAnalysis,
                                   SinglePhenomenonValidation):
    """Validation of a single circuit composition phenomenon.
    Validation is against reference data that provide experimental data
    as a function of layer. This base class may be used for validation
    composition of any brain region that is composed of layers.
    """
    spatial_parameters = Field(
        __name__ = "spatial_parameters",
        __type__=set,
        __typecheck__ = Field.typecheck.collection(LayerIndex),
        __doc__ = """A composition phenomenon must be measured as a function
        of location in the brain --- spatial_parameters represent these
        locations. For example, you may want cell density as a function of
        'CorticalLayer'."""
    )

    implementations = {}

    def __init__(self, *args, **kwargs):
        """
        This validation will be made against multiple datasets. Each dataset
        should provide a 'Record' as specified below.

        Arguments
        ------------------------------------------------------------------------
        validation_data :: Either[
        ~ Record[datasets :: Dict[String -> MeasurementRecord],
        ~        primary  :: String],#of datasets, which one is primary to compare againsts.
        ~ Dict[String -> MeasurementRecord], #or a single dataset.
        ] where
        MeasurementRecord = List[Record[measurement_label :: String,
        ~                               region_label :: String,
        ~                               data :: DataFrame["mean", "std],
        ~                               citation :: Either[Citation, String],
        ~                               what :: String]]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        """
        super().__init__(*args, **kwargs)

    
    @property
    def set_parameters(self, dataframe):
        """Set the parameters in the index of dataframe to
        match the model's measurements.

        Notes
        ------------------------------------------------------------------------
        Who should decide how the plots, report, etc. look like? Customization
        of reports, things like what symbols to represent 'Layer' with, Roman
        or Hindu numerals? Should the customization be model side or
        experimental side? 

        Currently we let the modeler control the reports as it seemed natural
        at the time of the current implementation. However, this conflicts with
        a central theme of our design:

        THE EXPERIMENTAL SIDE IMPLEMENTS VALIDATION.

        After all, experiments are used to test our
        beliefs about phenomena, and a model is just a complex and sophisticated
        way of encoding our beliefs. Here, we think of beliefs as a joint
        probability distribution of all the possible ways this world may be
        organized.

        As a result we have to handle the awkward situation of having the model
        adapter handle experimental data to have their parameter representation
        match that of the model's own measurement.
        We plan the shift of this responsibility from modeling side to the side 
        of experimenting to be our next big change.
        """
        raise NotImplementedError()

    @property
    def validation_data(self):
        """Override"""
        if not hasattr(self, "reference_data"):
            raise Exception("Validation test case {} does not use reference data"\
                            .format(self.__class__.__name__))
        data = self.reference_data.data

        if not isinstance(data, dict):
            if not isinstance(data, pd.DataFrame):
                raise AttributeError(
                    "Reference data is not a pandas DataFrame, but {}\n{}"\
                    .format(type(data).__name__, data)
                )
            return data

        assert(isinstance(data, dict))
        if len(data) == 1:
            self.logger.devnote(
                self.logger.get_source_info(),
                "Only one element in dict.",
                "We assume that element is a pandas DataFrame."""
            )
            return list(data.values())[0]

        dataset_names = [k for k in data.keys()]

        fdf = flatten({n: data[n].data for n in dataset_names},
                      names=["dataset"])[["mean", "std"]]

        return fdf.set_index(
            pd.MultiIndex(levels=fdf.index.levels, labels=fdf.index.labels,
                          names=[n.lower() for n in fdf.index.names])
        )

    @property
    def validation_datasets(self):
        """Return validation data as a dict."""
        data = (self.reference_data.data
                if isinstance(self.reference_data.data, Record) else
                self.reference_data.data)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {d.label: d for d in data}
        return {data.label: data}

    def data_description(self):
        """Describe the experimental data used for validation."""
        return self.reference_data.description

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
            validated_phenomenon = self.phenomenon,
            validation_image_dir = ".", #keep image dir relative
            validation_image_name = plot_name,
            author = self.author,
            caption = self.get_caption(model_measurement),
            validation_datasets = self.validation_datasets,
            is_pass = verdict == Verdict.PASS,
            is_fail = verdict == Verdict.FAIL,
            pvalue = pval
        )

    @property
    def primary_dataset(self):
        """..."""
        return self.reference_data.primary_dataset

    @property
    def spatial_parameter_group(self):
        """..."""
        return ParameterGroup(tuple(self.spatial_parameters))


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
