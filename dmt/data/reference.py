"""..."""

import pandas as pd
from dmt.data\
    import ReferenceData
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.utils.collections\
    import Record\
    ,      take
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError


class MultiReferenceData(
        ReferenceData):
    """Reference data with multiple datasets, one of which will be primary"""
    
    datasets=\
        Field(
            __name__="datasets",
            __type__=dict,
            __typecheck__=Field.typecheck.mapping(str, ReferenceData),
            __doc__="""'datasets' should map dataset label to
            a ReferenceData instance.""")
    primary=\
        Field(
            __name__="primary",
            __type__=str,
            __doc__="""If this ReferenceData holds more than one dataset, 
            then you may choose a primary dataset out of your multiple 
            datasets. If this field is set to a string, then its value 
            must be the label of one of the datasets in this
            ReferenceData.""")

    def __init__(self,
            datasets,
            *args, **kwargs):
        """..."""
        self.logger.info(
            self.logger.get_source_info(),
            "initialize {} instance with kwargs".format(
                self.__class__.__name__),
            *["\t{}: {}".format(k, v) for k, v in kwargs.items()] )
        self.logger.debug(
            self.logger.get_source_info(),
            "datasets: {}".format(datasets),
            "primary dataset: {}".format(
                kwargs.get("priamry", None)))
        super().__init__(
            datasets=datasets,
            data={dataset_label: dataset_data.data
                  for dataset_label, dataset_data in datasets.items()},
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

    def add_dataset(self,
            dataset_label,
            dataset):
        """Add a dataset to the existing ones."""
        if dataset_label in self.datasets:
            raise ValueError(
                "{} already has data set labeled {}".format(
                    self,
                    dataset_label))
        assert\
            isinstance(dataset, ReferenceData)
        self.datasets[dataset_label]=\
            dataset
        self.data[dataset_label]=\
            dataset.data
        return self

    @property
    def primary_dataset(self):
        """..."""
        if not hasattr(self, "primary"):
            return self.data

        if isinstance(self.primary, pd.DataFrame):
            return self.primary

        return self.get_dataset(self.primary)
