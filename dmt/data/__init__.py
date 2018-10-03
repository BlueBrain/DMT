"""Data from experiments."""

from abc import abstractmethod
import pandas as pd
from dmt.aii import Callable, AIBase
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.collections import Record

@document_fields
class ReferenceData(WithFCA):
    """Data from experiments, to be used as reference data in a validation."""
    description = Field(
        __name__="description",
        __type__=str,
        __default__="Not Available",
        __doc__="You may provide a description for your ReferenceData."
    )
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

    def _is_location(self, data_value):
        """...
        'data_value' will be passed as a keyword argument to '__init__'.
        For now we assume that 'data_value' is location of data if and only if
        it is a string. The user may override this method to accommodate their
        data locations.
        """
        return isinstance(data_value, str)

    def _load_from_location(self, data_location):
        """Load data from a location
        We provide a default implementation that makes a trivial check.
        The concrete implementation needs to complete this implementation only
        if data will be loaded from a location.
        """
        if not self._is_location(data_location):
            self.logger.alert(
                self.logger.get_source(),
                "Cannot load data from argument 'data_location' {}"
                .format(data_location)
            )
            return None
        raise NotImplementedError(
            "Complete this implementation to load data from a location."
        )


    @abstractmethod
    def _get_data(self, kwarg_dict):
        """get data from kwargs."""
        pass

    @abstractmethod
    def primary_dataset(self):
        """..."""
        pass
