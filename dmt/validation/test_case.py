"""Validation test case.
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of ValidationTestCase will accept a data object.
"""

from abc import abstractmethod
from dmt.aii import AdapterInterfaceBase
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, document_fields

@document_fields
class ValidationTestCase(AdapterInterfaceBase):
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adapter.requires', and use them like this,
    'measurement_data = self.get_measurement_data(model, parameters)'.

    Attributes
    ----------------------------------------------------------------------------
    author :: Author #The author of this validation
    """

    author = Field(
        __name__ = "author",
        __type__ = Author,
        __doc__ = """Author of the validation code."""
    )
    def __init__(self, *args, **kwargs):
        """A validation test case can be initialized either with a validation
        data set, or the directory location of a validation data set, or none,
        but not both.
        """
        self.__validation_data = kwargs.get('validation_data', None)
        if (self.__validation_data is None and
            'validation_data_location' in kwargs):
            if not hasattr(self, '_load_validation_data'):
                raise NotImplementedError(
                    "To load data from a directory location\
                    you must implement method '_load_validation_data' for {}"\
                    .format(self.__class__.__name__)
                )
            self.__validation_data\
                = self._load_validation_data(kwargs['validation_data_location'])

        self.author = kwargs.get('author', Author.anonymous)
        super(ValidationTestCase, self).__init__(*args, **kwargs)

    @property
    def validation_data(self):
        """Data to validate a model against.
        However, you are allowed to create a validation without data!!!
        ------------------------------------------------------------------------
        Notes
        ------------------------------------------------------------------------
        We talk of validation being against real data.
        ------------------------------------------------------------------------
        """
        if self.__validation_data is None:
            raise Exception("Test case {} does not use validation data"\
                            .format(self.__class__.__name__))
        return self.__validation_data

    @property
    def reference_data(self):
        """Another term for validation data."""
        return self.validation_data

    @property
    def test_data(self):
        """Another term for validation data."""
        return self.validation_data

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """A ValidationTestCase is a callable.
        In a concrete ValidationTestCase implementation,
        the first argument must be a model.
        *args, and **kwargs may contain parameters to be passed to the model."""
        pass

