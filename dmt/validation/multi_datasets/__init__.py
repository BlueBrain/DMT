"""A validation that uses multiple datasets."""

from abc import abstractmethod
import os
import numpy as np
from dmt.aii import adaptermethod, reportattribute
from dmt.validation.test_case import ValidationTestCase
from dmt.vtk.judgment import Verdict
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


    class Report:
        """The report for multi-dataset validations.
        We have defined 'Report' as an inner class here.
        After we have implemented a few different reports,
        we can think of a better approach to integrating reporting into a
        validation."""
        def __init__(self, image="validation_plot.png",
                     caption="not-provided",
                     datasets=[],
                     verdict=Verdict.NA,
                     p_value=np.nan):
            self.image = image
            self.caption = caption
            self.datasets = datasets
            self.verdict = verdict
            self.p_value = p_value

        def save(self, template=None):
            """Save this report.
            --------------------------------------------------------------------

            Parameters
            --------------------------------------------------------------------
            template :: A Cheetah template.
            --------------------------------------------------------------------

            Notes
            --------------------------------------------------------------------
            If a template is provided, it will be used. We assume that the
            template is a Cheetah template. If a template is not provided,
            contents of a Report will be saved to the disk separately.
            """
            pass
        
    @adaptermethod
    def get_measurement(model_adapter, model):
        """Get measurement from the model with the model adapter.
        ------------------------------------------------------------------------
        Return :: Record(label :: String, data :: DataFrame)
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    def evaluation(self, model_measurement):
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
        report = self.evaluation(model_measurement)

        return report.save(output_dir_path, report_file_name)


