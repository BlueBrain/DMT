"""Data from experiments."""

from abc import ABC, abstractmethod
import pandas as pd
from dmt.aii import Callable, AIBase
from dmt.vtk.utils.descriptor import Field, document_fields, WithFCA
from dmt.vtk.utils.exceptions import MissingRequiredKeywordArgument
from dmt.vtk.utils.collections import Record

@document_fields
class ReferenceData(WithFCA):
    """Data from experiments, to be used as reference data in a validation."""
    description = Field.Optional(
        __name__="description",
        __type__=str,
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
    primary = Field.Optional(
        __name__="primary",
        __typecheck__=Field.typecheck.either(str, pd.DataFrame),
        __doc__="""If this ReferenceData holds more than one dataset, then
        you may choose a primary dataset out of your multiple datasets.
        If this field is set to a string, then its value must be the label
        of one of the datasets in this ReferenceData."""
    )
    def __init__(self, *args, **kwargs):
        """..."""
        data_primary = self._get_data(kwargs)
        self.data = data_primary[0]
        p = data_primary[1]
        if p:
            kwargs.update({"primary": p})
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

    def _get_data(self, kwarg_dict):
        """..."""
        if "data" not in kwarg_dict:
            raise MissingRequiredKeywordArgument("data")
        data_and_primary = kwarg_dict["data"]

        if not self._is_location(data_and_primary):
            if isinstance(data_and_primary, Record):
                try:
                    return (data_and_primary.datasets, data_and_primary.primary)
                except AttributeError:
                    pass
            else:
                data = data_and_primary
        else:
            data = self._load_from_location(data_value)

        primary = kwarg_dict.get("primary", None)
        return (data, primary)

    def get_dataset(self, dataset_name):
        """..."""
        try:
            return self.data.get(dataset_name, None)
        except AttributeError:
            pass

        if isinstance(self.data, pd.DataFrame):
            try:
                return self.data.xs(dataset_name, level="dataset")
            except AttributeError:
                pass
        return None

    @property
    def primary_dataset(self):
        """..."""
        if not hasattr(self, "primary"):
            return self.data

        if isinstance(self.primary, pd.DataFrame):
            return self.primary

        return self.get_dataset(self.primary)
