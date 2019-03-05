"""..."""

import pandas as pd
from dmt.data\
    import ReferenceData
from dmt.vtk.utils.pandas\
    import flatten
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.measurement.condition\
    import Condition
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
        self._measurement_parameters_values = None
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

    @property
    def single_data_frame(self):
        """All reference datasets flattened to a single dataframe."""
        data=\
            self.data
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, dict):
            dataset_names=\
                list(data.keys())
            flattened_dataframe=\
                flatten(
                    {name: data[name].data for name in dataset_names},
                    names=["dataset"]
                )[["mean", "std"]]
            return\
                flattened_dataframe.set_index(
                    pd.MultiIndex(
                        levels=flattened_dataframe.index.levels,
                        labels=flattened_dataframe.index.labels,
                        names=[name.lower()
                               for name in flattened_dataframe.index.names]))

        raise AttributeError(
            "Reference data is neither a 'dict', nor a pandas DataFrame",
            "It is a {}\n{}"\
            .format(type(data).__name__, data))

    @property
    def measurement_parameters_values(self):
        """a list of dict{parameter_label: parameter_value}"""
        if self._measurement_parameters_values is None:
            data_index_dataframe=\
                pd.MultiIndex.to_frame(
                    self.single_data_frame.index
                )[self.measurement_parameters]
            self._measurement_parameters_values={
                Condition(
                    list(
                        row[1].to_dict().items()))\
                .sorted_pairs_tuple
                for row in data_index_dataframe.iterrows()}
        return self._measurement_parameters_values

    def contains(self,
            measurement_parameters_value):
        """Does this data contain measurement_parameters_values.

        Arguments
        --------------
        measurement_parameters_values :: dict(param_label -> param_value)
        """
        return any(
            all(
                measurement_parameters_value.get(param_label, None)\
                == param_value
                for param_label, param_value in param_label_value_pairs)
            for param_label_value_pairs in self.measurement_parameters_values)
