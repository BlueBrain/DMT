"""Report the result of an analysis or a validation."""
import os
import pandas as pd
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.descriptor import is_field, WithFCA, Field
from dmt.vtk.utils.utils import get_file_name_base, timestamp
from dmt.vtk.utils.logging import Logger

class Report(
        WithFCA):
    """Report base class.
    A report may have fields (dmt.vtk.utils.descriptor.Field)
    """
    model_measurement=\
        Field(
            __name__="model_measurement",
            __type__=pd.DataFrame,
            __doc__="Result of measuring the model.")

    def __init__(self, *args, **kwargs):
        """Add attributes from kwargs to this report instance.
        The value of each report attribute in 'kwargs' must be a string."""
        #self.__dict__.update(kwargs)
        self.__report_attributes__ = kwargs.keys()
        self.__report_dict__ = {k: v for k, v in kwargs.items()}
        super().__init__(
            *args, **kwargs)
            

    @classmethod
    def update_doc(cls):
        """Add __doc__ of fields to that of this class"""
        field_docs=\
            "\n\nFields\n"
        field_docs+=\
            70 * "-" + "\n"
        field_attrs=\
            []
        for attr, value in cls.__dict__.items():
            if is_field(value):
                field_attrs.append(attr)
                field_docs += attr + "\n"
                field_docs += "    type {}\n".format(value.__type__)
                field_docs += "    {}\n".format(value.__doc__)
        field_docs+=\
            70 * "-" + "\n"
        cls.__doc__+=\
            field_docs
        return field_attrs


    def _save_default(self,
            output_dir_path,
            file_name_base):
        """A method to save the report,
        in case 'save' that uses a template fails
        This method will save each attribute of the report as a string.
        """
        file_name = file_name_base + ".txt"
        report_file_path = os.path.join(output_dir_path, file_name)

        with open(report_file_path, 'w') as f:
            for attribute in self.__report_attributes__:
                f.write(attribute + '\n')
                f.write("    {}\n".format(getattr(self, attribute)))

        return report_file_path

    def save_measurement(self,
            output_dir_path,
            sep=","):
        """..."""
        file_path=\
            os.path.join(
                output_dir_path,
                "model_measurement.csv")
        self.model_measurement.reset_index()\
            .to_csv(file_path, sep=sep, index=False)
        return\
            file_path

    def save(self,
            output_dir_path,
            report_file_name=None):
        """Save the results --- this uses the default method.
        Please over-ride it where you want to define your own custom save.
        """
        file_name_base = get_file_name_base(report_file_name)
        return self._save_default(output_dir_path, file_name_base)
                                  
    @classmethod
    def get_output_location(cls,
            output_dir_path=None,
            with_timestamp=True):
        """Determine the location where to save the report."""
        odp = output_dir_path if output_dir_path else os.getcwd()
        if with_timestamp:
            daytime = timestamp()
            odp = os.path.join(odp, daytime.day, daytime.time)

        odp = os.path.join(odp)
        
        if not os.path.exists(odp):
            os.makedirs(odp)

        return odp
