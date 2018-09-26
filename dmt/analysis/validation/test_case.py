""" Some base classes for validations.

Implementation Notes
--------------------------------------------------------------------------------
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of a validation class will accept a data object.
"""

from abc import ABC, abstractmethod
from dmt.aii import Callable, AIBase
from dmt.analysis import Analysis
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import ClassAttribute, Field, document_fields
from dmt.vtk.phenomenon import Phenomenon

@document_fields
class ValidationTestCase(Analysis):
    """A validation test case.
    Instructions on implementing a ValidationTestCase
    -------------------------------------------------
    Provide validation logic in method '__call__'.
    Mark all model measurements that validation needs
    with decorator '@adaptermethod', and use them like any other method.
    """
    author = Field(
        __name__ = "author",
        __type__ = Author,
        __doc__  = """Author of the validation code."""
    )
    def __init__(self, *args, **kwargs):
        """A validation test case can be initialized either with a validation
        data set, or the directory location of a validation data set, or none,
        but not both.

        Keyword Arguments
        ------------------------------------------------------------------------
        primary_dataset :: String #the key into validation_data dict that
        ~                         #corresponds to the dataset to use to evaluate
        ~                         #p-values or other validation statistics.
        """
        self._validation_data = self.get_validation_data(**kwargs)
        self._primary_dataset = kwargs.get("primary_dataset", None)#used to track which of validation data is primary
        self.author = kwargs.get('author', Author.anonymous)
        super(ValidationTestCase, self).__init__(*args, **kwargs)

    @classmethod
    def get_validation_data(cls, **kwargs):
        """Read validation data from keyword arguments.
        This method is called by the initializer."""
        if "validation_data" in kwargs:
            return kwargs["validation_data"]
        data_location = kwargs.get("validation_data_location", None)
        if data_location is not None:
            if not hasattr(self, "_load_validation_data"):
                raise NotImplementedError(
                    "To load data from a directory location\
                    you must implement method '_load_validation_data' for {}"\
                    .format(cls.__name__)
                )
            return self._load_validation_data(data_location)
        return None

    @property
    def validation_data(self):
        """Data to validate a model against.
        However, you are allowed to create a validation without data!!!

        Note
        ------------------------------------------------------------------------
        We talk of validation being against real data.
        The form of the data will be known only to the concrete implementation
        of ValidationTestCaseBase. Here we assume that data is expected by the
        caller as it is.

        Please, feel free to specialize this method to your implementation.
        """
        if self._validation_data is None:
            raise Exception("Test case {} does not use validation data"\
                            .format(self.__class__.__name__))
        return self._validation_data

    @property
    def primary_dataset(self):
        """Primary validation dataset

        Note
        ------------------------------------------------------------------------
        We assume that self._validation_data is a singleton, and return it as
        also the primary data set to validate with.

        A deriving class may override.
        """
        return self._validation_data

    @property
    def reference_data(self):
        """Another term for validation data."""
        return self.validation_data

    @property
    def test_data(self):
        """Another term for validation data."""
        return self.validation_data

    @abstractmethod
    def data_description(self):
        """Describe the data used for this validation.
        For example, describe where the data were obtained from."""
        pass

    @abstractmethod
    def __call__(self, model, *args, **kwargs):
        """A ValidationTestCase is a callable.
        In a concrete ValidationTestCase implementation,
        the first argument must be a model.
        *args, and **kwargs may contain parameters to be passed to the model."""
        pass


#class ValidationTestCase(ValidationTestCaseBase, AIBase):
#    """"Just a class that mixes two.
#    ValidationTestCaseBase is useful by itself. Mixing in AIBase
#     will add adapter interface goodies."""
#    pass


@document_fields
class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.
    """
    validated_phenomenon = Field(
        __name__ = "validated_phenomenon",
        __type__ = Phenomenon,
        __doc__  = "The phenomenon that is measured for this validation."
    )
    def __init__(self, *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        if 'validated_phenomenon' in kwargs:
            self.validated_phenomenon = kwargs['validated_phenomenon']
        super().__init__(*args, **kwargs)

