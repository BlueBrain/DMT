"""Circuit composition test cases, when the composition is measured by layer."""
from abc import ABC, abstractmethod
import os
from dmt.validation.test_case import ValidationTestCase
from dmt.aii import adaptermethod
from dmt.vtk.utils.collections import Record
from dmt.vtk.reporting.cheetah import ReportWithCheetahTemplate
from dmt.vtk.author import Author
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.plotting import golden_figure
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.descriptor import Field
from dmt.validation.single_phenomemon import SinglePhenomenonValidation
from dmt.vtk.judgment.verdict import Verdict
from neuro_dmt.validations.circuit.composition import layer_composition 


class CompositionReport(ReportWithCheetahTemplate):
    """A reporting class that will be used for all composition validations.
    The html produced by the Cheetah Template used here will display a plot
    for the validation, with a caption, metadata about the authors and their
    affiliation, and the status of the validation --- i.e. whether the model
    passed the validation or not.

    Once fully developed, we must move this class to a location from where it
    can be loaded for more general use-cases.

    Notes
    ----------------------------------------------------------------------------
    Cheetah template must be placed in a directory named 'templates' in the
    same directory as this file.
    """
    __template_loc__ = os.path.join(os.path.dirname(__file__),
                                    "templates",
                                    "validation_with_plot.cheetah")


class CellDensity(SinglePhenomenonValidation):
    """CellDensity is a 'unit' test case for validation.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    i.e., the pandas DataFrame passed around as a measurement must have
    a column labeled 'region'.

    Attributes
    ----------------------------------------------------------------------------
    author :: Author #The author of this validation.
    validated_phenomenon :: Phenomenon / String # measured for this validation
    region_type :: String #To know the region type in measurements, layer, etc.
    """

    region_type = "Cortical Layer"

    def __init__(self, validation_data, *args, **kwargs):
        """This initializer is written as a generic initializer,
        that should be moved to a base class once we can identify all the
        functionality that is common among cell composition validations.
        ------------------------------------------------------------------------

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(measurement_label :: String,
        ~                              region_label :: String,
        ~                              data :: DataFrame["region", "mean", "std"],
        ~                              citation :: Citation,
        ~                              what     :: String)]

        #This validation will be made against multiple datasets.
        #The type of 'validation_data' above specifies what is expected of each
        #validation dataset.
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #optional where the report will be saved
        report_file_name :: String #optional name of the report file
        plot_customization :: dict #optional dict to customize validation plot
        ------------------------------------------------------------------------
        """
        self.p_value_threshold = kwargs.get('p_value_threshold', 0;05)
        self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
        self.report_file_name = kwargs.get('report_file_name', 'report.html')
        self.plot_customization = kwargs.get('plot_customization', {})

        kwargs['validation_data']\
            = validation_data
        kwargs['validated_phenomenon']\
            = Phenomenon("Cell Density", "Count of cells in a unit volume")
        kwargs['author']\
            = Author(name="Vishal Sood", affiliation="EPFL", user_id=1)
        
        super(CellDensity, self).__init__(*args, **kwargs)


    @adaptermethod
    def get_cell_density(circuit_model):
        """Get cell density for a circuit.
        This method must be defined for the model adapter class that will
        interpret a circuit model to be validated.

        Parameters
        ------------------------------------------------------------------------
        circuit_model :: ModelCircuit

        Return
        ------------------------------------------------------------------------
        Record(phenomenon :: Phenomenon, #that was measured
        ~      measurement_label :: String, #used as label for the measurement
        ~      region_label :: String, #label for regions in data
        ~      data :: DataFrame["region", "mean", "std"],
        ~      method :: String)
        """
        pass


    @adaptermethod
    def get_anatomically_ordered(circuit_model, data_frame):
        """Get an anatomically ordered data frame.
        This method must be defined for the model adapter class that will
        interpret a circuit model to be validated.

        Parameters
        ------------------------------------------------------------------------
        circuit_model :: ModelCircuit
        data_frame :: DataFrame #with column 'region' to be used for ordering

        Return
        ------------------------------------------------------------------------
        DataFrame # Anatomically ordered data-frame

        Examples
        ------------------------------------------------------------------------
        If the region is CorticalDepth the order can be
        ['L1', 'L2', 'L3', 'L4', 'L5', 'L6'] or it's reverse
        """
        pass

    @adaptermethod
    def get_label(circuit_model):
        """Get a label for the circuit model.

        Parameters
        ------------------------------------------------------------------------
        circuit_model :: ModelCircuit
        """
        pass


    def plot(self, model_measurement, *args, **kwargs):
        """Plot the data."""
        plotting_datas = [model_measurement] + self.validation_data
        image_path\
            = layer_composition.plot_bars(plotting_datas, *args, **kwargs)
        #return Record(image_path=image_path,
        return image_path

    def get_caption(self, model_measurement):
        """A placeholder --- we will have to define methods for the model
        adapter to get real content for this caption.

        Implemented Notes
        ------------------------------------------------------------------------
        This method does not belong here. It should be moved to a more general
        location.
        """
        return "{} is plotted. {}\n Method: {} "\
            .format(self.model_measurement.phenomenon.title,
                    self.model_measurement.phenomenon.description,
                    self.model_measurement.method)

    def __call__(self, circuit_model, *args, **kwargs):
        """Make CellDensity callable."""
        output_dir_path = kwargs.get('output_dir_path', self.output_dir_path)
        report_file_name = kwargs.get('report_file_name', self.report_file_name)

        model_measurement = self.model_adapter.get_cell_density(circuit)

        model_label = self.model_adapter.get_label(circuit_model)

        p_val = layer_composition.probability_of_validity(
            model_measurement, self.validation_data[0]
        )
        verdict = layer_composition.get_verdict(p_val, self.pvalue_threshold)

        report = CompositionReport(
            validated_phenomenon=self.validated_phenomenon.title,
            validation_image_path=self.plot(model_measurement),
            author_name=self.author.name,
            author_affiliation=self.author.affiliation,
            caption=self.get_caption(model_measurement),
            validation_datasets=self.validation_data,
            is_pass=verdict == Verdict.PASS,
            is_fail=verdict == Verdict.FAIL,
            p_value=p_val
        )
        return report

