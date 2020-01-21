"""
Test develop HBP bindings for DMT.
"""
import numpy as np
import numpy.testing as npt
import pandas as pd
from scipy import stats
import sciunit
from sciunit.models import Model
from sciunit.capabilities import Capability
from sciunit.errors import ObservationError
from sciunit.scores import Score
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.analysis import Analysis
from dmt.model.interface import Interface
from .. import *


class ArithmeticInterface(Interface):
    """
    The interface that a test can use to analyze a model.
    """
    def addition(self, x, y):
        """
        Add two numbers

        Arguments
        -------------
        x :: Number
        y :: Number
        """
        raise NotImplementedError

    def subtraction(self, x, y):
        """
        Subtract the second number from the first.

        Arguments
        -------------
        x :: Number
        y :: Number
        """
        raise NotImplementedError

    def multiplication(self, x, y):
        """
        Multiply two numbers

        Arguments
        -------------
        x :: Number
        y :: Number
        """
        raise NotImplementedError

    def division(self, x, y):
        """
        Divide the first number by the second.

        Arguments
        -------------
        x :: Number
        y :: Number
        """
        raise NotImplementedError


class ArithmeticAnalysis(Analysis):
    """
    Analyze a model that provides an implementation of arithmetic.
    """
    AdapterInterface = ArithmeticInterface

    pstar = Field(
        """
        Value for the threshold p-value.
        """,
        __default_value__=0.05)
    observation = Field(
        """
        A pandas dataframe
        """)

    def get_measurement(self, model, adapter):
        """
        Get measurement from a model.

        Arguments
        -----------

        """
        xs = self.observation.x.values
        ys = self.observation.y.values
        return pd.DataFrame(dict(
            x = xs,
            y = ys,
            addition = adapter.addition(model, xs, ys),
            subtraction = adapter.subtraction(model, xs, ys),
            multiplication = adapter.multiplication(model, xs, ys),
            division = adapter.division(model, xs, ys)))

    def statistical_summary(self, measurement):
        """
        A statistical summary for a measurement on a model.
        """
        return measurement

    def statistical_test(self, observation, prediction):
        """
        Compute a statistical score that matches
        a model prediction against an experimental observation.
        """
        pvalues = np.array([
            stats.ttest_ind(
                observation.addition.values,
                prediction.addition.values).pvalue,
            stats.ttest_ind(
                observation.subtraction.values,
                prediction.subtraction.values).pvalue,
            stats.ttest_ind(
                observation.multiplication.values,
                prediction.multiplication.values).pvalue,
            stats.ttest_ind(
                observation.division.values,
                prediction.division.values).pvalue
            ])
        log_pvalues = np.log(pvalues)
        chisq = -2 * np.sum(log_pvalues)
        pooled_pvalue = 1. - stats.chi2.cdf(chisq, 2 * len(pvalues))
        return pd.Series({
            "pvalue": pooled_pvalue,
            "description": "Chi-square for pooled p-values"})

    def __call__(self, model, adapter):
        """
        Call me.
        """
        prediction = self.get_measurement(model, adapter)
        return self.statistical_score(
            self.observation,
            prediction)


class BadArithmeticModel:
    """
    A model that will not pass.
    """
    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return y - x

    def times(self, x, y):
        return x * y

    def by(self, x, y):
        return y / x


class GoodArithmeticModel:
    """
    A model that should pass.
    """
    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return x - y

    def times(self, x, y):
        return x * y

    def by(self, x, y):
        return x / y


class ArithmenticModelAdapter:
    """
    Adapt a model that implements arithmetic to the requirements of
    analysis' interface.
    """
    def addition(self, model, x, y):
        return model.plus(x, y)

    def subtraction(self, model, x, y):
        return model.minus(x, y)

    def multiplication(self, model, x, y):
        return model.times(x, y)

    def division(self, model, x, y):
        return model.by(x, y)


class AdaptedModel(WithFields):
    """
    A model adapted by an adapter.
    """
    model = Field(
        """
        The model to be adapted.
        """)
    adapter = Field(
        """
        The adapter for the model.
        """)



def test():
    xs = np.random.uniform(1.e-9, 1., size=20)
    ys = np.random.uniform(1.e-9, 1., size=20)
    observation = pd.DataFrame(dict(
        x = xs,
        y = ys,
        addition = xs + ys,
        subtraction = xs - ys,
        multiplication = xs * ys,
        division = xs / ys))
    analysis = ArithmeticAnalysis(observation=observation)
    adapter = ArithmenticModelAdapter()
    test = SciUnitValidationTest(
        analysis,
        adapter,
        observation = observation )
    BadModel = SciUnitModel(BadArithmeticModel, ArithmeticInterface)
    assert test.judge(BadModel())

    GoodModel = SciUnitModel(GoodArithmeticModel, ArithmeticInterface)
    assert test.judge(GoodModel())


