"""Report the result of an analysis or a validation."""
import os

class Report:
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

    @classmethod
    def get_file_name_base(file_name=None):
        """Get the base from a file name, stripping away it's suffix."""
        return ("report" if file_name is None else
                '_'.join(file_name.split('.')[0:-1]).strip().replace(' ', '_'))

    def save(self, output_dir_path, report_file_name=None):
        """Save the results --- this uses the default method.
        Please over-ride it where you want to define your own custom save.
        """
        file_name_base = self.__class__.get_file_name_base(report_file_name)
        return self._save_default(output_dir_path, file_name_base)
                                  
