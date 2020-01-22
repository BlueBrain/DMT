"""
Adapt neuro_dmt code to use SciUnit to provide validations
to the HBP Validation Framework.
"""
import pandas as pd
import sciunit
from sciunit.errors import ObservationError
from sciunit.scores import BooleanScore
from dmt.tk.field import Field, lazyfield

def SciUnitCapability(interface):
    """
    Convert an Interface to a sciunit.Capability.
    """
    name = interface.__name__.replace("Interface", "Capability")
    return type(name, (sciunit.Capability, ), dict(interface.__dict__))

def SciUnitModel(interface, Model):
    """
    Convert a model type to scinuit.Model

    Arguments
    -------------
    interface :: `dmt.Interface` that lists methods required for an analysis.
    Model :: A model type (i.e. class object) to be analyzed by an `Analysis`,
    ~        whose required methods are specified in `interface`.
    """
    return type(
        Model.__name__,
        (Model, sciunit.Model, SciUnitCapability(interface)),
        {})


class SciUnitValidationTest(sciunit.Test):
    """
    Common code for HBP Validation Framework friendly tests.
    """

    def __init__(self, analysis, adapter, observation,
                 name=None,
                 pstar = 0.05,
                 **params) :
        """
        Initialize...
        """
        self._analysis = analysis
        self._adapter = adapter
        self._pstar = pstar
        super().__init__(observation, name=name, **params)

    def validate_observation(self, observation):
        """
        Validate an observation
        """
        if not isinstance(observation, pd.DataFrame):
            raise ObservationError("Observation was not a pandas.DataFrame")
        return None

    def compute_score(self, observation, prediction):
        """
        Compute a score comparing model prediction to experimental observation.
        """
        try:
            statistical_test_result =\
                self._analysis.statistical_test(observation, prediction)
            if statistical_test_result.pvalue < self._pstar:
                return BooleanScore(False)
        except:
            pass
        return BooleanScore(True)

    def validate_observation(self, observation):
        """
        Validate an observation.
        """
        if not isinstance(observation, pd.DataFrame):
            raise ObservationError(
                "Expected a pandas.DataFrame, received type of observation:"\
                .format(type(observation)))
        return None

    def generate_prediction(self, model):
        """
        Generate a prediction on the model.
        This method is required by sciunit.Test to do its job.
        """
        measurement = self._analysis.get_measurement(model, self._adapter)
        return self._analysis.statistical_summary(measurement)

    def _as_sciunit_model(self, model):
        """
        Make sure that model is an instance of sciunit.Model.
        """
        if isinstance(model, sciunit.Model):
            return model
        try:
            interface = self._analysis.AdapterInterface
        except AttributeError as error:
            raise TypeError("""
            This {} instance's analysis ({} instance) does not have
            an `AdapterInterface`:
            \t {}""".format(
                self.__class__.__name__,
                self._analysis.__class__.__name__,
                error))
        model.__class__ = SciUnitModel(interface, model.__class__)
        return model

    def judge(self, model, **kwargs):
        """
        Override to allow models not derived from `sciunit.Model`.

        model :: Model instance to be validated.
        **kwargs :: Keyword arguments excepted by a `sciunit.Test` instance:
        ~           1. skip_incapable :: Boolean (defaults to False)
        ~           2. stop_on_error :: Boolean (defaults to True)
        ~           3. deep_error :: Boolean (defaults to False)
        """
        return super().judge(self._as_sciunit_model(model), **kwargs)
