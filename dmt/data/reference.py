"""..."""

from abc import abstractmethod
import pandas as pd
from dmt.data import ReferenceData
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.utils.collections import Record

class MultiReferenceData(
        ReferenceData):
    """Reference data with multiple datasets, one of which will be primary"""
    
    primary=\
        Field.Optional(
        __name__="primary",
            __typecheck__=Field.typecheck.either(str, pd.DataFrame),
            __doc__="""If this ReferenceData holds more than one dataset, 
            then you may choose a primary dataset out of your multiple 
            datasets. If this field is set to a string, then its value 
            must be the label of one of the datasets in this
            ReferenceData.""")
    data=\
        Field(
            __name__ = "data",
            __typecheck__=Field.typecheck.either(
                Field.typecheck.mapping(str, Record),
                Field.typecheck.mapping(str, dict)),
            __doc__="""A dict that maps labels to datasets that are 
            represented as a Record.""")

    def __init__(self,
            data,
            *args, **kwargs):
        """..."""
        self.logger.info(
            self.logger.get_source_info(),
            "initialize {} instance with kwargs".format(
                self.__class__.__name__),
            *["\t{}: {}".format(k, v) for k, v in kwargs.items()] )

        data_and_primary=\
            self.load(data)
        self.logger.debug(
            self.logger.get_source_info(),
            "data and primary should be a dictionary: \n {}".format(
                data_and_primary))
        super().__init__(
            data=data_and_primary["datasets"],
            primary=data_and_primary["primary"],
            *args, **kwargs)

    def get_dataset(self,
            dataset_name):
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
