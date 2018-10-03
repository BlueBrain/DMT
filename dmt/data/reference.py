"""..."""

import pandas as pd
from dmt.data import ReferenceData
from dmt.vtk.utils.exceptions import MissingRequiredKeywordArgument
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.utils.collections import Record

class MultiReferenceData(ReferenceData):
    """Reference data with multiple datasets, one of which will be primary"""
    
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
            if "description" not in kwargs:
                try:
                    kwargs["description"] = p.what
                except AttributeError:
                    pass

        super().__init__(*args, **kwargs)

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
            data = self._load_from_location(data_and_primary)

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
