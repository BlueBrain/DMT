"""Base classes for analyses."""

from abc import ABC, abstractmethod
import os
from dmt.model import Callable, AIBase
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.logging import Logger, with_logging

@with_logging(Logger.level.STUDY)
@document_fields
class Analysis(WithFCA, AIBase):
    """"Just a class that mixes two.
    AnalysisBaseClass is useful by itself. Mixing in AIBase
     will add adapter interface goodies."""

    phenomena = Field(
        __name__="phenomenon",
        __typecheck__=Field.typecheck.collection(Phenomenon),
        __doc__="Phenomena analyzed.")
    
    author = Field(
        __name__="author",
        __type__=Author,
        __default__=Author.anonymous,
        __doc__="""Author of this analysis.""")
    
    report_file_name = Field.Optional(
        __name__="report_file_name",
        __type__=str,
        __default__="report.html",
        __doc__="We assume that by default all reports will be saved as htmls")

    outou

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_report(self, *args, **kwargs):
        """..."""
        pass

    @abstractmethod
    def get_measurement(self, circuit_model):
        """Get the measurement to be validated."""
        pass


    @abstractmethod
    def get_label(self, model):
        """Get a label for the measurement validated."""
        pass

    def __call__(self, model, *args, **kwargs):
        """An Analysis is a callable.
        In the concrete Analysis implementation,
        the first argument must be the model to be analyzed,
        and args and kwargs may contain relevant parameters.

        We provide a default implementation here. You can define your
        Analysis or Validaiton against it's requirements: i.e methods
        get_measurement and get_report.
        Or override.
        """
        model_measurement = self.get_measurement(model)
        report = self.get_report(model_measurement)

        save = kwargs.get('save', False) #Or should we save by default?
        if save:
            try:
                odp = self.output_dir_path
            except AttributeError as e:
                self.logger.alert(
                    self.logger.get_source_info(),
                    """Did not find attibute 'output_dir_path' in {} instance"""\
                    .format(self.__class__.__name__),
                    "\t AttributeError: {}".format(e)
                )
                odp = os.getcwd()

            try:
                fname = self.report_file_name
            except AttributeError as e:
                self.logger.alert(
                    self.logger.get_source_info(),
                    """Did not find attibute 'report_file_name' in {} instance"""\
                    .format(self.__class__.__name__),
                    "\t AttributeError: {}".format(e)
                )
                fname = "report.html"
                
            report.save(
                output_dir_path=os.path.join(odp, "report"),
                report_file_name=fname
            )
        return report
