"""Data from experiments."""

from abc import abstractmethod
import pandas as pd
from dmt.model import Callable, AIBase
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.collections import Record

@document_fields
class ReferenceData(
        WithFCA):
    """Data from experiments, or a reference model,
    to be used as reference data in a model comparison,
    or an experimental validation."""
    data=\
        Field(
            __name__="data",
            __type__=object,
            __typecheck__=Field.typecheck.any(
                pd.DataFrame,
                Record,
                Field.typecheck.mapping(str, pd.DataFrame),
                Field.typecheck.mapping(str, Record),
                Field.typecheck.mapping(str, dict)),
            __doc__="""Attribute 'value' of ReferenceData is the actual data.
            We cannot set type of 'value'. It may either be a pandas
            dataframe""")
    description=\
        Field(
            __name__="description",
            __type__=str,
            __default__="Reference data",
            __doc__="Describe this reference data instance.")

    def __init__(self,
            *args, **kwargs):
        """..."""
        if "data" not in kwargs:
            super().__init__(
                *args,
                data=self.load(*args, **kwargs),
                **kwargs)
        else:
            super().__init__(
                *args, **kwargs)

    def _is_location(self,
            data_value):
        """...
        'data_value' will be passed as a keyword argument to '__init__'.
        For now we assume that 'data_value' is location of data if and only if
        it is a string. The user may override this method to accommodate their
        data locations.
        """
        return isinstance(data_value, str)

    @abstractmethod
    def _load_from_object(self, data):
        """Load data from an object that contains data."""
        pass

    @abstractmethod
    def _load_from_location(self, data):
        """..."""
        pass

    def load(self, data, *args, **kwargs):
        """Default method that assumes that loading from location
        results in a data-object that can be loaded as reference data.
        """
        self.logger.debug(
            self.logger.get_source_info(),
            "load data in  ReferenceData, from \n {}".format(data))

        if not self._is_location(data):
            try:
                return self._load_from_object(data)
            except TypeError as e:
                self.logger.alert(
                    self.logger.get_source_info(),
                    "{}: {}".format(type(e), e),
                    "\t{} object data is probably not the required type",
                    "\t{}".format(e))
        return self._load_from_location(data)
        
    @property
    @abstractmethod
    def primary_dataset(self):
        """..."""
        pass

    @property
    def representative_dataset(self):
        """..."""
        return self.primary_dataset
    
