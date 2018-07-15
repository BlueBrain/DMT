"""Validation test case.
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of ValidationTestCase will accept a data object.
"""

from abc import abstractmethod
from dmt.aii import AdapterInterfaceBase

class ValidationTestCase(AdapterInterfaceBase):
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adapter.requires', and use them like this,
    'measurement_data = self.get_measurement_data(model, parameters)'.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        self.__data = kwargs.get('data', None)
        super(ValidationTestCase, self).__init__(self, *args, **kwargs)
            

    @property
    def data(self):
        """Data stored to validate a model against.
        However, you are allowed to create a validation without data!!!"""
        if self.__data is None:
            raise Exception("Validation test case {} does not use data"\
                            .format(self.__class__.__name__))
        return self.__data

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """A ValidationTestCase is a callable.
        In a concrete ValidationTestCase implementation,
        the first argument must be a model.
        *args, and **kwargs may contain parameters to be passed to the model."""
        pass

