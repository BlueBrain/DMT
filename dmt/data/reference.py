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
    
    primary=\
        Field(
            __name__="primary",
            __type__=str,
            #__typecheck__=Field.typecheck.either(str, pd.DataFrame),
            __doc__="""If this ReferenceData holds more than one dataset, 
            then you may choose a primary dataset out of your multiple 
            datasets. If this field is set to a string, then its value 
            must be the label of one of the datasets in this
            ReferenceData.""")
    # data=\
    #     Field(
    #         __name__ = "data",
    #         __typecheck__=Field.typecheck.either(
    #             Field.typecheck.mapping(str, Record),
    #             Field.typecheck.mapping(str, dict)),
    #         __doc__="""A dict that maps labels to datasets that are 
    #         represented as a Record.""")

    def __init__(self,
            data=None,
            *args, **kwargs):
        """..."""
        if not data:
            raise Exception(
                "initializer argument data cannot be None.")
        self.logger.info(
            self.logger.get_source_info(),
            "initialize {} instance with kwargs".format(
                self.__class__.__name__),
            *["\t{}: {}".format(k, v) for k, v in kwargs.items()] )
        datasets = self.load(data)
            
        self.logger.debug(
            self.logger.get_source_info(),
            "datasets loaded: {}".format(datasets))
        super().__init__(
            data=datasets,
            *args, **kwargs)

        def _is_location(self,
            data_value):
            """...
            'data_value' will be passed as a keyword argument to '__init__'.
            For now we assume that 'data_value' is location of data if and only if
            it is a string. The user may override this method to accommodate their
            data locations.
            """
            if super()._is_location(data_value):
                return True
            if isinstance(data_value, list) and len(data_value) > 0:
                if super()._is.location(data_value[0]):
                    return True
                return False
    
    def _load_from_location(self,
            data_locations):
        """...
        Arguments
        ---------------
        data_location :: dict{label: location}
        """
        self.logger.info(
            self.logger.get_source_info(),
            """load_from_location in {}""".format(__file__))
        if not isinstance(data_locations, dict):
            raise ValueError(
                "A MultiReferenceData requires a dict of data locations.")
        if len(data_locations) == 0:
            raise ValueError(
                "No locations in dict data_location: {}"\
                .format(data_location))
        if not isinstance(list(take(1, data_locations.values()))[0], str):
            raise ValueError(
                """A MultiReferenceData requires a dict{str: str}
                that maps dataset label --> dataset location.""")
        return{
            label: self._load_one_from_location(
                label, location)
            for label, location in data_locations.items()}
        # return self._load_from_object(
        #     Record(
        #         datasets={
        #             label: self._load_one_from_location(
        #                 label, location)
        #             for label, location in data_locations.items()},
        #         primary=self.primary))

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
