"""Base classes for analyses."""

from abc import ABC, abstractmethod
import os
from dmt.model import AIBase
from dmt.vtk.author import Author
from dmt.vtk.plotting import Plot
from dmt.vtk.utils.descriptor import Field, WithFCA, document_fields
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.logging import Logger, with_logging

class Registry:
    """Store your subclass instances"""
    def __init__(self, cls, *args, **kwargs):
        """..."""
        self.register_type = cls
        self.__known_instances = []
        super().__init__(*args, **kwargs)

    def insert(self, instance):
        """Insert an subclass instance"""
        if not isinstance(instance, self.register_type):
            return None
        self.__known_instances.append(instance)
        
    def find(self, **kwargs):
        """..."""
        def __satisfies(instance):
            """..."""
            return all(
                hasattr(instance, attr) and getattr(instance, attr) == value
                for attr, value in kwargs.items() )
        return [
            instance for instance in self.__known_instances
            if __satisfies(instance)]


@with_logging(Logger.level.STUDY)
@document_fields
class Analysis(WithFCA, AIBase):
    """"Just a class that mixes two.
    AnalysisBaseClass is useful by itself. Mixing in AIBase
     will add adapter interface goodies."""

    analysis_type = Field(
        __name__="analysis_type",
        __type__=str,
        __default__="analysis",
        __doc__="To be used to save reports and figures.")

    phenomena = Field(
        __name__="phenomena",
        __typecheck__=Field.typecheck.collection(Phenomenon),
        __doc__="Phenomena analyzed.")

    author = Field(
        __name__="author",
        __type__=Author,
        __default__=Author.anonymous,
        __doc__="""Author of this analysis.""")
    
    Plotter = Field.Optional(
        __name__="Plotter",
        __typecheck__=Field.typecheck.subtype(Plot),
        __doc__="""A subclass of {} to be used plot the results of
        this validation.""".format(Plot))

    plot_customization = Field.Optional(
        __name__="plot_customizaion",
        __type__=dict,
        __doc__="A dict containing customization of the plot.")

    output_dir_path = Field(
        __name__="output_dir_path",
        __type__=str,
        __doc__="Where the report will be saved to.")

    report_file_name = Field.Optional(
        __name__="report_file_name",
        __type__=str,
        __doc__="By default, we assume that the report should be saved as an html.")

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)
        self.registry = Registry(Analysis)
        self.registry.insert(self)

    def _get_output_dir(self):
        """..."""
        odp = getattr(self, "output_dir_path", None)
        return os.path.join(
            odp if odp else os.getcwd(),
            self.analysis_type)

    @abstractmethod
    def get_report(self, *args, **kwargs):
        """..."""
        pass

    @abstractmethod
    def get_measurement(self, model, *args, **kwargs):
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
        model_measurement = self.get_measurement(model, *args, **kwargs)
        report = self.get_report(model_measurement)

        if kwargs.get('save_report', False):
            try:
                fname = self.report_file_name
            except AttributeError as e:
                self.logger.alert(
                    self.logger.get_source_info(),
                    """Did not find attibute 'report_file_name' in {} instance"""\
                    .format(self.__class__.__name__),
                    "\t AttributeError: {}".format(e))
                fname = "report.html"

            report.save(
                output_dir_path=self._get_output_dir(),
                report_file_name=fname)

        return report



class OfSinglePhenomenon:
    """Mixin single phenomenon into an analysis or a validation."""

    phenomenon = Field(
        __name__="phenomenon",
        __type__=Phenomenon,
        __doc__="""A SinglePhenomenonValidation can have only one Phenomenon
        that is measured, validated, and reported.""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        self.phenomenon = phenomenon
        kwargs["phenomena"] = {phenomenon}
        super().__init__(*args, **kwargs)

    def _get_output_dir(self):
        """..."""
        group_label_path\
            = os.path.join(
                self.phenomenon.group if self.phenomenon.group else "ungrouped",
                self.phenomenon.label)
        try:
            return os.path.join(
                super()._get_output_dir(),
                group_label_path)
        except AttributeError:
            return group_label_path

    def get_caption(self, model_measurement):
        """Caption that will be shown below the validation plot.

        Implementation Notes
        ------------------------------------------------------------------------
        Measurement method must be known to produce an informative caption.
        However this information is available only to the model adapter, and
        not to the class representing the validation itself. The author of the
        concrete implementation of SinglePhenomenonValidation will have to
        determine where to get the information required to produce a caption.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(phenomenon :: Phenomenon#that was measured,
        ~                           label :: String,#used to label the measureemnt
        ~                           region_label :: String,#for regions measured
        ~                           data :: DataFrame["region", "mean", "std"],
        ~                           method :: String #how measurement was made.])
        """
        return "{} is plotted. {}\n Method: {}"\
            .format(self.phenomenon.title,
                    self.phenomenon.description,
                    model_measurement.method)


class OfMultiPhenomena:
    """Mixin multi phenomena into an analysis or validation."""

    phenomena = Field(
        __name__="phenomena",
        __typecheck__=Field.typecheck.collection(Phenomenon),
        __doc__="Phenomena analyzed.")

    def __init__(self,
            phenomena,
            *args, **kwargs):
        """..."""
        self.phenomena = phenomena
        super().__init__(*args, **kwargs)

    def _get_output_dir(self):
        """..."""
        group_label_path\
            = os.path.join(
                *Phenomenon.group_label(
                    *Phenomenon.sorted(self.phenomena)) )
        try:
            return os.path.join(
                super()._get_output_dir(),
                group_label_path)
        except AttributeError:
            return group_label_path

    def get_caption(self,
            model_measurement):
        """Caption that will be shown below the validation plot.

        Implementation Notes
        ------------------------------------------------------------------------
        Measurement method must be known to produce an informative caption.
        However this information is available only to the model adapter, and
        not to the class representing the validation itself. The author of the
        concrete implementation of SinglePhenomenonValidation will have to
        determine where to get the information required to produce a caption.

        Parameters
        ------------------------------------------------------------------------
        model_measurement :: Record(phenomenon :: Phenomenon#that was measured,
        ~                           label :: String,#used to label the measureemnt
        ~                           region_label :: String,#for regions measured
        ~                           data :: DataFrame["region", "mean", "std"],
        ~                           method :: String #how measurement was made.])
        """
        sorted_phenomena = Phenomenon.sorted(self.phenomena)
        group, label\
            = Phenomenon.group_label(
                *sorted_phenomena)
        return "{} are plotted. {}\n Method: {}".format(
            label,
            Phenomenon.make_description(
                *sorted_phenomena),
            model_measurement.method)


class SinglePhenomenonAnalysis(
        OfSinglePhenomenon,
        Analysis):
    """A partially mixed Mixin"""
    def __init__(phenomenon, *args, **kwargs):
        """..."""
        super().__init__(phenomenon, *args, **kwargs)

