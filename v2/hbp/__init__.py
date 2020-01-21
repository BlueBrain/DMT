"""
Adapt neuro_dmt code to use SciUnit to provide validations
to the HBP Validation Framework.
"""
import pandas as pd
import sciunit
from sciunit.models import Model
from sciunit.capabilities import Capability
from sciunit.errors import ObservationError
from sciunit.scores import BooleanScore
from dmt.tk.field import Field, lazyfield

def SciUnitCapability(interface):
    """
    Convert an Interface to a sciunit.Capability.
    """
    name = interface.__name__.replace("Interface", "Capability")
    return type(name, (Capability, ), dict(interface.__dict__))

def SciUnitModel(model, adapter_interface):
    """
    Convert a model to a scinuit.Model
    """
    capability = SciUnitCapability(adapter_interface)
    return type(model.__name__, (model, Model, capability), {})



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
        statistical_test_result =\
            self._analysis.statistical_test(observation, prediction)
        if statistical_test_result.pvalue < self._pstar:
            return BooleanScore(False)
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
