"""A validation that uses multiple datasets."""

from abc import abstractmethod
import os
from dmt.aii import adaptermethod, reportattribute
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.utils.collections import Record

class MultiDataSetValidationTestCase(ValidationTestCase):
    """Validate a model against multiple datasets at once."""

    def __init__(self, validation_data, *args, **kwargs):
        """Initialize either with a list of multiple validation datasets,
        or a path to the location from where this data may be loaded. Either
        of these may be passed in as keyword arguments.
        ------------------------------------------------------------------------
        
        Arguments
        ------------------------------------------------------------------------
        validation_data :: List[Record(label :: String,
        ~                              citation :: Citation,
        ~                              what :: String,
        ~                              data :: DataFrame)]
        ------------------------------------------------------------------------

        Keyword Arguments
        ------------------------------------------------------------------------
        p_value_threshold :: Float #optional
        output_dir_path :: String #where the report will be saved
        ------------------------------------------------------------------------
        ~                                
        """
        self.p_value_threshold = kwargs.get('p_value_threshold', 0.05)
        self.output_dir_path = kwargs.get('output_dir_path', os.getcwd())
        self.report_file_name = kwargs.get('report_file_name', 'report.html')
        kwargs['validation_data'] = validation_data
        super(MultiDataSetValidationTestCase, self).__init__(*args, **kwargs)


    @adaptermethod
    def get_measurement(model_adapter, model):
        """Get measurement from the model with the model adapter.
        ------------------------------------------------------------------------
        Return :: Record(label :: String, data :: DataFrame)
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    def get_judgment(self, model_measurement):
        """Judge how valid a model's measurement is against validation data.
        ------------------------------------------------------------------------
        Return
        ------------------------------------------------------------------------
        A report that can be saved to the disk, or displayed on an interactive
        platform such as the desktop or a webpage.
        ------------------------------------------------------------------------
        """
        pass

    def __call__(self, model, *args, **kwargs):
        """A common call method that can be applied to any validation,
        that tests the model against multiple experimental data sets."""

        output_dir_path = kwargs.get('output_dir_path', self.output_dir_path)
        report_file_name = kwargs.get('report_file_name', self.report_file_name)
        model_measurement = self.model_adapter.get_measurement(model)
        report = self.get_judgment(model_measurement)

        report_file_path = os.path.join(output_dir_path, report_file_name)
        print("Generating {}".format(report_file_path))
        return report.save(report_file_path)


