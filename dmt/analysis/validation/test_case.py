""" Some base classes for validations.

Implementation Notes
--------------------------------------------------------------------------------
We will assume that data is attached to a validation, i.e. the author of the
validation knows the format of the data that she is going to validate a model
against. The initializer of a validation class will accept a data object.
"""

from abc import abstractmethod
from dmt.aii import Callable, AIBase
from dmt.data import ReferenceData
from dmt.analysis import Analysis
from dmt.vtk.author import Author
from dmt.vtk.utils.descriptor import Field, document_fields
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
    ReferenceDataType = Field.Optional(
        __name__="reference_data",
        __typecheck__=Field.typecheck.subtype(ReferenceData),
        __doc__="If not provided, assume validation does not use ReferenceData"
    )
    def __init__(self, *args, **kwargs):
        """..."""
        if "validation_data" in kwargs:
            kwargs.update({"data": kwargs["validation_data"]})
        super().__init__(*args, **kwargs)

        if hasattr(self, "ReferenceDataType"):
            self.reference_data = self.ReferenceDataType(*args, **kwargs)



    @property
    def get_validation_data(self):
        """..."""
        return self.reference_data.data if self.reference_data else None

    @property
    @abstractmethod
    def primary_dataset(self):
        """..."""
        pass

@document_fields
class SinglePhenomenonValidation(ValidationTestCase):
    """Validation of a single phenomenon.
    A single phenomenon will be measured for a model, and compared against
    validation data. P-value will be used as a validation criterion.
    """
    def __init__(self, *args, **kwargs):
        """Validated phenomenon must be set by the deriving class."""
        if 'validated_phenomenon' in kwargs:
            kwargs["phenomena"] = {kwargs['validated_phenomenon']}
        if 'phenomenon' in kwargs:
            kwargs["phenomena"] = {kwargs['phenomenon']}
        super().__init__(*args, **kwargs)
