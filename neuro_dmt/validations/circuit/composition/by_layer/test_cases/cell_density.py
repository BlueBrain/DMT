"""Circuit composition test cases, when the composition is measured by layer."""
from abc import ABC, abstractmethod
import os
from dmt.validation.test_case import ValidationTestCase
from dmt.aii import adaptermethod
from dmt.vtk.utils.collections import Record
from dmt.vtk.reporting.cheetah import ReportWithCheetahTemplate
from dmt.vtk.author import Author

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
                                    "report_html_template.cheetah")


class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.

    Attributes
    ----------------------------------------------------------------------------
    validated_phenomenon :: Phenomenon / String 
    """

    validated_phenomenon = None

    def __init__(self, *args, **kwargs):
        """Before initializing, check that the concrete implementation of
        SinglePhenomenonValidation has set it's validated_phenomenon."""

        if validated_phenomenon is None:
            raise NotImplementedError(
                "class {} must provide a validated_phenomenon"\
                .format(self.__class__.__name__)
            )


class CellDensity(ValidationTestCase):
    """CellDensity is a 'unit' test case for validation.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    i.e., the pandas DataFrame passed around as a measurement must have
    a column labeled 'region'.

    Attributes
    ----------------------------------------------------------------------------
    author :: Author #The author of this validation.
    phenomenon :: Phenomenon #The phenomenon measured for this validation
    """
    author = Author(name="Vishal Sood",
                    affiliation="EPFL",
                    user_id=1)

    def __init__(self, validation_data, *args, **kwargs):
        """This initializer is written as a generic initializer,
        that should be moved to a base class once we can identify all the
        functionality that is common among cell composition validations.
        ------------------------------------------------------------------------

        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(label    :: String,
        ~                              citation :: Citation,
        ~                              what     :: String,
        ~                              data     :: DataFrame)]

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

        kwargs['validation_data'] = validation_data
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
        Record(label :: String, #to be used as label for the measurement
        ~      data :: DataFrame["region", "mean", "std"])
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


    def __call__(self, circuit_model, *args, **kwargs):
        """Make CellDensity callable."""
        output_dir_path = kwargs.get('output_dir_path', self.output_dir_path)
        report_file_name = kwargs.get('report_file_name', self.report_file_name)

        model_measurement = self.model_adapter.get_cell_density(circuit)

        model_label = self.model_adapter.get_label(circuit_model)
        report = CompositionReport(
            validated_phenomenon=repr(self.phenomenon)
        )

