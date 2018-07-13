"""Validation test case.
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of ValidationTestCase will accept a data object.
"""

from abc import abstractmethod
from dmt import adapter

class ValidationTestCase(metaclass=adapter.AIMeta):
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adapter.requires', and use them like this,
    'measurement_data = self.get_measurement_data(model, parameters)'.
    """
    __metaclass__ = adapter.AIMeta #for Python 2 --- irrelevant in Python 3

    def __init__(self, data=None, model_adapter=lambda model_object: model_object):
                 
        """
        Parameters
        ----------
        model_adapter :: Model -> AdaptedModel
        a callable that returns an adapted model."""
        self.__data = data
        self.get_adapted_model = model_adapter

    @property
    def data(self):
        """Data stored to validate a model against.
        However, you are allowed to create a validation without data!!!"""
        if self.__data is not None:
            return self.__data

        raise Exception("Validation test case {} does not use data"\
                        .format(self.__class__.__name__))

    @property
    def adapter(self):
        """A concrete implementation of this ValidationTestCase's
        AdapterInterface."""
        return self._adapter

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """A ValidationTestCase is a callable.
        In a concrete ValidationTestCase implementation,
        the first argument must be a model.
        *args, and **kwargs may contain parameters to be passed to the model."""
        pass

