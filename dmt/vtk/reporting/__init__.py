"""Report the result of an analysis or a validation."""

from abc import ABC, abstractmethod
import os

class Report(ABC):
    """Report base class."""

    def __init__(self, **kwargs):
        """Add attributes from kwargs to this report instance.
        The value of each report attribute in 'kwargs' must be a string."""
        self.__dict__.update(kwargs)
        self.__report_attributes__ = kwargs.keys()
        self._report_dict = {attr: self.__dict__[attr]
                             for attr in self.__report_attributes__}

    def _save_default(self, output_dir_path, file_name_base):
        """A method to save the report,
        in case 'save' that uses a template fails.
        This method will save each attribute of the report as a string.
        """
        file_name = file_name_base + ".txt"
        report_file_path = os.path.join(output_dir_path, file_name)

        with open(report_file_path, 'w') as f:
            for attribute in self.__report_attributes__:
                f.write(attribute + '\n')
                f.write((len(attribute) + 4) * '-')
                f.write(str(self.__dict__[attribute]))

        return report_file_path
