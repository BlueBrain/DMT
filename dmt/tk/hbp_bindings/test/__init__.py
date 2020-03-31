# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop HBP bindings for DMT.
"""
import numpy as np
from numpy import testing as npt
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
    measurement_parameters = Field(
        """
        A pandas dataframe
        """)

    def get_measurement(self, model, adapter):
        """
        Get measurement from a model.

        Arguments
        -----------

        """
        xs = self.measurement_parameters.x.values
        ys = self.measurement_parameters.y.values
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
        def is_close(xs, ys):
            return np.all(np.isclose(xs, ys))
        is_pass =\
            all([
                is_close(prediction.addition, observation.addition),
                is_close(prediction.subtraction, observation.subtraction),
                is_close(prediction.multiplication, observation.multiplication),
                is_close(prediction.division, observation.division)])

        return pd.Series({
            "pass": is_pass,
            "description": "Some sort of comparison..."})

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


class ArithmeticModelAdapter:
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


def test():
    xs = np.random.uniform(1.e-9, 1., size=20)
    ys = np.random.uniform(1.e-9, 1., size=20)
    measurement_parameters = pd.DataFrame(dict(x=xs, y=ys))
    observation = pd.DataFrame(dict(
        x = xs,
        y = ys,
        addition = xs + ys,
        subtraction = xs - ys,
        multiplication = xs * ys,
        division = xs / ys))
    analysis = ArithmeticAnalysis(measurement_parameters=measurement_parameters)
    adapter = ArithmeticModelAdapter()
    test = SciUnitValidationTest(
        analysis,
        observation = observation )

    abam = AdaptedModel(BadArithmeticModel(), adapter)
    assert not test.judge(abam).get_raw()
    BadModel = SciUnitModel(analysis.AdapterInterface, BadArithmeticModel)
    assert not test.judge(BadModel(adapter)).get_raw()

    agam = AdaptedModel(GoodArithmeticModel(), adapter)
    assert test.judge(agam).get_raw()
    GoodModel = SciUnitModel(analysis.AdapterInterface, GoodArithmeticModel)
    assert test.judge(GoodModel(adapter)).get_raw()


