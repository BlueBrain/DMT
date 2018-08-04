"""Handlers of Cheetah templates."""

from abc import ABC, abstractmethod
import os
from Cheetah.Template import Template
from dmt.vtk.reporting import Report


class ReportWithCheetahTemplate(Report):
    """A wrapper around a Cheetah template, that encapsulates their logic,
    and exposes a minimal uniform interface to templates.
    A full working implementation will require either a Cheetah template, or
    the location of a template. This class cannot be initialized unless one of
    the class attributes  __template__, __template_loc__ has been defined.
    These may be defined either by a deriving implementation or explicitly.

    Attributes
    ----------------------------------------------------------------------------
    __template__ :: str #a Cheetah template set by concrete implementation.
    __template_loc__ :: str # template location set by concrete implementation.
    ----------------------------------------------------------------------------

    Implementation Notes
    ----------------------------------------------------------------------------
    As we develop this class, we will learn protocols for what a reporter
    should provide. As a result we can adapt another template system.
    """
    __template__ = None
    __template_loc__ = None

    @classmethod
    def _load_template(template_location):
        """Load a Cheetah template from the provided location.

        Remarks
        ------------------------------------------------------------------------
        While defining the required template as a string within the body of the
        concrete implementation of ReportWithCheetahTemplate could be more
        elegant, it is more convenient to load this template from a file on the
        disk. This is a utility classmethod to load templates from files.
        """
        with open(template_location, 'r') as f:
            return f.read()
        raise Exception(
            "Template could not be loaded from {}".format(template_location)
        )
        
    
    def __init__(self, **kwargs):
        """Add attributes from kwargs to a cheetah template.
        The attributes provided in 'kwargs' should provide the arguments
        required by the template string.
        This class cannot be initialized unless one of the class attributes
        __template__, __template_loc__ has been defined. These may be defined
        either by a deriving implementation or explicitly.

        Parameters
        ------------------------------------------------------------------------
        kwargs :: KeywordArguments # required fields by __template__
        """
        cls = self.__class__
        if cls.__template__ is not None:
            self.template = cls.__template__
        elif cls.__template_loc__ is not None:
            self.template = cls._load_template(cls.__template_loc__)
        else:
            raise Exception(
                "{} provides neither a template, nor a template locationd!!!"\
                .format(cls.__name__)
            )
        super(ReportWithCheetahTemplate, self).__init__(self, **kwargs)

    def save(self, output_dir_path, report_file_name=None):
        """Save report to disc.

        Parameters
        ------------------------------------------------------------------------
        output_dir_path :: String #directory where report artefacts should go
        report_file_name :: String #name of the file to use for this report
        ------------------------------------------------------------------------
        Implementation Notes
        ------------------------------------------------------------------------
        This method tries to create a (html) string using its class' template
        and save that to the disc. If this fails, a default method is run that
        will save each of report's attributes to the disc in a text file.
        """
        print("Saving report at {}".format(output_dir_path))
        file_name_base =  ("report" if report_file_name is None 
                           else report_file_name.split('.')[0].strip())

        file_name = file_name_base + ".html"
        report_file_path = os.path.join(output_dir_path, file_name)

        try:
            t = Template(self.template, searchList=self.__dict__)
            with open(report_file_path, 'w') as f:
                f.write(str(t))
        except Exception as ex: #convert the following to a warning
            print("WARNING!!!\n\
            While loading the template, or saving the report\
            something went wrong.\n" + str(ex) +
            "will proceed saving the contents to disc as text.")
            self._save_default(output_dir_path, file_name_base)
