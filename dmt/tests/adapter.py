"""Test and develop adapters for models and validation requirements"""

from dmt import adapter
from dmt.validation import TestCase


@adapter.adapt
class TestIntegerMath(TestCase):

    @adapter.provided
    def add(self, x, y):
        """Add two numbers x and y"""
        pass

    @adapter.provided
    def sub(self, x, y):
        """Sub two numbers x and y"""
        pass

    def __call__(self, model):
        adapted_model = self.get_adapted_model(model)
        assert(adapted_model.add(1, 1) == 2)
        assert(adapted_model.sub(2, 1) == 1)
        print("PASS")
        return True

class BadIntegerMathModel:
    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x + y

class GoodIntegerMathModel:
    def plus(self, x, y):
        return x + y
    def minus(self, x, y):
        return x - y

@adapter.implementation(TestIntegerMath.AdapterInterface)
class TestIntegerMathAdapter:
    def __init__(self, model):
        self.model = model

    def add(self, x, y):
        return self.model.plus(x, y)

    def sub(self, x, y):
        return self.model.minus(x, y)


tim = TestIntegerMath(TestIntegerMathAdapter)
