"""Report the result of an analysis or a validation."""
import os
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.descriptor import is_field
from dmt.vtk.utils.utils import get_file_name_base, timestamp
from dmt.vtk.utils.logging import Logger

class Report:
    """Report base class.
    A report may have fields (dmt.vtk.utils.descriptor.Field)"""
    def __init__(self, *args, **kwargs):
        """Add attributes from kwargs to this report instance.
        The value of each report attribute in 'kwargs' must be a string."""
        #self.__dict__.update(kwargs)
        self.__report_attributes__ = kwargs.keys()
        self.__report_dict__ = {}
        for attr, value in self.__class__.__dict__.items():
            if is_field(value):
                try:
                    value = kwargs[attr]
                except:
                    raise RequiredKeywordArgumentError(attr)
                setattr(self, attr, value) #this will validate the value
                self.__report_dict__[attr] = value #this will be a validated value!
            

    @classmethod
    def update_doc(cls):
        """Add __doc__ of fields to that of this class"""
        field_docs = "\n\nFields\n"
        field_docs += 70 * "-" + "\n"
        field_attrs = []
        for attr, value in cls.__dict__.items():
            if is_field(value):
                field_attrs.append(attr)
                field_docs += attr + "\n"
                field_docs += "    type {}\n".format(value.__type__)
                field_docs += "    {}\n".format(value.__doc__)
        field_docs += 70 * "-" + "\n"
        cls.__doc__ += field_docs
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
