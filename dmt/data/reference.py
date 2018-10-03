"""..."""

import pandas as pd
from dmt.data import ReferenceData
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
    data = Field(
        __name__ = "data",
        __typecheck__=Field.typecheck.either(
            Field.typecheck.mapping(str, Record),
            Field.typecheck.mapping(str, dict)
        ),
        __doc__="""A dict that maps labels to datasets that are represented
        as a Record."""
    )

    def __init__(self, *args, **kwargs):
        """..."""
        self.logger.info(
            self.logger.get_source_info(),
            "initialize {} instance with kwargs".format(self.__class__.__name__),
            *["\t{}: {}".format(k, v) for k, v in kwargs.items()]
        )
        (data, primary) = self._get_data(*args, **kwargs)
        self.data = data
        if primary:
            self.primary = primary
        if "description" in kwargs:
            self._description = kwargs["description"]

        super().__init__(*args, **kwargs)

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
