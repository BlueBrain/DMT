"""Data from experiments."""

from abc import abstractmethod
import pandas as pd
from dmt.model import Callable, AIBase
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.collections import Record

@document_fields
class ReferenceData(WithFCA):
    """Data from experiments, to be used as reference data in a validation."""
    data = Field(
        __name__="data",
        __type__=object,
        __typecheck__=Field.typecheck.any(
            pd.DataFrame, Record,
            Field.typecheck.mapping(str, pd.DataFrame),
            Field.typecheck.mapping(str, Record)
        ),
        __doc__="""Attribute 'value' of ReferenceData is the actual data.
        We cannot set type of 'value'. It may either be a pandas 
        """
    )

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @property
    def description(self):
        """Describe this data. A default behavior is provided.
        Please override and provide a good description of your data."""
        return "Not Available"

    def _is_location(self, data_value):
        """...
        'data_value' will be passed as a keyword argument to '__init__'.
        For now we assume that 'data_value' is location of data if and only if
        it is a string. The user may override this method to accommodate their
        data locations.
        """
        return isinstance(data_value, str)


    @abstractmethod
    def load(self, *args, **kwargs):
        """get data."""
        pass

    @abstractmethod
    def primary_dataset(self):
        """..."""
        pass
