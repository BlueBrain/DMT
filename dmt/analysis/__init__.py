"""Base classes for analyses."""

import os
from abc\
    import abstractmethod
import traceback
from dmt.model\
    import AIBase
from dmt.vtk.author\
    import Author
from dmt.vtk.plotting\
    import Plot
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA\
    ,      document_fields
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.measurement.parameter\
    import Parameter
from dmt.vtk.reporting\
    import Report
from dmt.vtk.utils.logging\
    import Logger\
    ,      with_logging

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

    analysis_type=\
        Field(
            __name__="analysis_type",
            __type__=str,
            __default__="analysis",
            __doc__="To be used to save reports and figures.")
    phenomena=\
        Field(
            __name__="phenomena",
            __typecheck__=Field.typecheck.collection(Phenomenon),
            __doc__="Phenomena analyzed.")
    measurement_parameters=\
        Field.Optional(
            __name__="measurement_parameters",
            __typecheck__=Field.typecheck.collection(Parameter),
            __doc__="""Parameters used to measure the phenomenon""")
    plotting_parameter=\
        Field.Optional(
            __name__="plotting_parameter",
            __type__=Parameter,
            __doc__="""Parameter that measurement data will be plotted
            against.""")
    plotted_parameters=\
        Field(
            __name__="plotted_parameters",
            __type__=list,
            __typecheck__=Field.typecheck.collection(str),
            __doc__="""Labels of parameters that will be plotted. Usually this 
            will be single value -- sometimes there may be more than one. For ,
            example in a cross-plot with model measurement data on the y-axis 
            and reference validation data on the x-axis, qll the measurement
            parameters get plotted.""",
            __default__ = [])
    author=\
        Field(
            __name__="author",
            __type__=Author,
            __default__=Author.anonymous,
            __doc__="""Author of this analysis.""")
    Plotter=\
        Field.Optional(
            __name__="Plotter",
            __typecheck__=Field.typecheck.subtype(Plot),
            __doc__="""A subclass of {} to be used plot the results of
            this validation.""".format(Plot))
    plot_customization=\
        Field.Optional(
            __name__="plot_customizaion",
            __type__=dict,
            __default__={},
            __doc__="A dict containing customization of the plot.")
    ReportType=\
        Field.Optional(
            __name__="ReportType",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(Report))
    output_dir_path=\
        Field(
            __name__="output_dir_path",
            __type__=str,
            __default__=os.getcwd(),
            __doc__="Where the report will be saved to.")
    report_file_name=\
        Field(
            __name__="report_file_name",
            __type__=str,
            __default__="report.html",
            __doc__="""By default, we assume that the report
            should be saved as an html.""")

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
    def get_report(self,
            model_measurement,
            *args, **kwargs):
        """Create a report for model_measurement"""
        pass

    @abstractmethod
    def get_measurement(self, model, *args, **kwargs):
        """Get the measurement to be validated."""
        pass

    @abstractmethod
    def get_label(self, model):
        """Get a label for the measurement validated."""
        pass

    def is_permissible(self,
            measurement_parameters_values):
        """Is the given condition valid?
        A default behavior (always permissible) is provided.
        The intended use is for validations, for which not all parameter
        value combinations need be measured. Only the values represented
        in validation data should be measured.

        Arguments
        --------------
        measurement_parameters_values :: Any[Condition, dict, pandas.Series].
        """
        return True

    def save_report(self,
            report,
            output_dir_path=""):
        """..."""
        output_dir_path=\
            output_dir_path if output_dir_path\
            else self._get_output_dir()
        try:
            fname = self.report_file_name
        except AttributeError as e:
            self.logger.alert(
                self.logger.get_source_info(),
                """Did not find attibute 'report_file_name' in {} instance"""\
                .format(self.__class__.__name__),
                "\t AttributeError: {}".format(e))
            fname = "report.html"
        return\
            report.save(
                output_dir_path=os.path.join(
                    output_dir_path),
                report_file_name=fname)

    def __call__(self,
            model,
            save_report=False,
            *args, **kwargs):
        """An Analysis is a callable.
        In the concrete Analysis implementation,
        the first argument must be the model to be analyzed,
        and args and kwargs may contain relevant parameters.

        We provide a default implementation here. You can define your
        Analysis or Validaiton against it's requirements: i.e methods
        get_measurement and get_report.
        Or override.
        """
        model_measurement=\
            self.get_measurement(
                model,
                *args,
                is_permissible=lambda condition: self.is_permissible(
                    condition.as_dict),
                **kwargs)
        report=\
            self.get_report(
                model_measurement,
                *args, **kwargs)
        if save_report:
            self.save_report(
                report,
                output_dir_path=self._get_output_dir(
                    model_measurement))
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

    def _get_output_dir(self,
            *args, **kwargs):
        """..."""
        group_label_path\
            = os.path.join(
                self.phenomenon.group if self.phenomenon.group else "ungrouped",
                self.phenomenon.label)
        try:
            return os.path.join(
                super()._get_output_dir(
                    *args, **kwargs),
                group_label_path)
        except AttributeError as aerr:
            self.logger.alert(
                self.logger.get_source_info(),
                "Encountered an AttributeError {}".format(aerr),
                traceback.format_exc(),
                "will return output directory based on the phenomenon \
                investigated")
            return group_label_path

    def get_caption(self,
            model_measurement,
            *args, **kwargs):
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
        model_measurement :: Record[
        ~    phenomenon :: Phenomenon#that was measured,
        ~    label :: String,#used to label the measureemnt
        ~    region_label :: String,#for regions measured
        ~    data :: DataFrame["region", "mean", "std"],
        ~    method :: String #how measurement was made.]
        """
        given_parameter_values=\
            "" if len(kwargs) == 0 else\
            "For " + ','.join([
                "{} {}".format(parameter, value)
                for parameter, value in kwargs.items()])
        return[
            "{} is plotted.".format(
                self.phenomenon.title),
            "Measurement method: {}".format(
                model_measurement.measurement_method),
            "Sampling method: {}".format(
                model_measurement.sampling_method),
            "Number samples: {}".format(
                model_measurement.sample_size),
            given_parameter_values]

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

