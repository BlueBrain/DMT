"""Data from experiments."""

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
        self.logger.debug(
            self.logger.get_source_info(),
            """initializer in ReferenceData""")
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

    @property
    def primary_dataset(self):
        """A default is provided,
        override if your ReferenceData is a MultiReferenceData"""
        return self.data

    @property
    def representative_dataset(self):
        """A default is provided,
        override if your ReferenceData is a MultiReferenceData."""
        try:
            return self.primary_dataset
        except AttributeError:
            return self.data
        return None
    
