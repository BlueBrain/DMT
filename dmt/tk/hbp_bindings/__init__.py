# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Adapt neuro_dmt code to use SciUnit to provide validations
to the HBP Validation Framework.
"""
import pandas as pd
import sciunit
from sciunit.errors import ObservationError
from sciunit.scores import BooleanScore
from dmt.tk.field import Field, lazyfield, WithFields

def SciUnitCapability(interface):
    """
    Convert an Interface to a sciunit.Capability.
    """
    name = interface.__name__.replace("Interface", "Capability")
    return type(name, (sciunit.Capability, ), dict(interface.__dict__))


class AdaptedModel:
    """
    Wrap an adapter around a model.
    """
    def __init__(self, model, adapter):
        self.model = model
        self.adapter = adapter

    def __getattr__(self, method):
        """..."""
        try:
            return getattr(self.model, method)
        except AttributeError as error_model:
            try:
                adapter_method = getattr(self.adapter, method)
                def adapted_method(*args, **kwargs):
                    return adapter_method(self.model, *args, **kwargs)
                return adapted_method
            except AttributeError as error_adapter:
                pass

        raise AttributeError(
            """
            Attribute {} not available on the model or its adapter.
            """.format(method))


def SciUnitModel(interface, Model):
    """
    Convert a model type to scinuit.Model

    Arguments
    -------------
    interface :: `dmt.Interface` that lists methods required for an analysis.
    Model :: A model type (i.e. class object) to be analyzed by an `Analysis`,
    ~        whose required methods are specified in `interface`.
    """
    WrappedModel = type(
        "{}{}".format("SciUnit", Model.__name__),
        (Model, sciunit.Model, SciUnitCapability(interface)),
        {})
    if issubclass(Model, AdaptedModel):
        return WrappedModel

    def __getattr__(self, method):
        """
        Try to call the method on the model or the adapter.
        """
        try:
            def method_adapted(*args, **kwargs):
                """delegate to adapter"""
                return getattr(self._adapter, method)(self, *args, **kwargs)
            return method_adapted
        except AttributeError as error_adapter:
            raise AttributeError(
                """
                {} not defined for the model {} or it's adapter {}
                """.format(
                    method,
                    self.__class__.__name__,
                    self._adapter.__class__.__name__))

    def __init__(self, adapter, *args, **kwargs):
        """..."""
        self.adapter = adapter
        super(WrappedModel, self).__init__(*args, **kwargs)

    WrappedModel.__getattr__ = __getattr__
    WrappedModel.__init__ = __init__
    return WrappedModel


class SciUnitValidationTest(sciunit.Test):
    """
    Common code for HBP Validation Framework friendly tests.
    """

    def __init__(self, analysis, observation,
                 name=None,
                 pstar = 0.05,
                 **params) :
        """
        Initialize...
        """
        self._analysis = analysis
        self._pstar = pstar
        super().__init__(observation, name=name, **params)

    def compute_score(self, observation, prediction):
        """
        Compute a score comparing model prediction to experimental observation.
        """
        if not hasattr(self._analysis, "statistical_test"):
            return BooleanScore(True)

        statistical_test_result =\
            self._analysis.statistical_test(observation, prediction)
        return BooleanScore(statistical_test_result["pass"])

    def validate_observation(self, observation):
        """
        Validate an observation.
        """
        if not isinstance(observation, pd.DataFrame):
            raise ObservationError(
                "Expected a pandas.DataFrame, received type of observation:"\
                .format(type(observation)))
        return None

    def generate_prediction(self, adapted_model):
        """
        Generate a prediction on the model.
        This method is required by sciunit.Test to do its job.
        """
        measurement = self._analysis.get_measurement(adapted_model,
                                                     adapted_model.adapter)
        return self._analysis.statistical_summary(measurement)

    def _as_sciunit_model(self, model):
        """
        Make sure that model is an instance of sciunit.Model.
        """
        if isinstance(model, sciunit.Model):
            return model

        interface = getattr(self._analysis, "AdapterInterface", None)
        if interface is None:
            raise TypeError("""
            This {} instance's analysis ({} instance) does not have
            an `AdapterInterface`.
            \t {}""".format(
                self.__class__.__name__,
                self._analysis.__class__.__name__))
        if not hasattr(model, "adapter"):
            raise TypeError("""
            No adapter attribute in model {}.
            """.format(model.__class__.__name__))

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
