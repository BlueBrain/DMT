"""Circuit data used for building and validating circuits
at the Blue Brain Project."""
from abc import abstractmethod
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.phenomenon import Phenomenon
from dmt.data.reference import MultiReferenceData
from neuro_dmt.measurement.parameter import\
    BrainCircuitSpatialParameter, CorticalLayer
from neuro_dmt.utils.brain_regions import BrainRegion

class BlueBrainCircuitCompositionData(MultiReferenceData):
    """Base class that describes circuit composition data used for validating
     Blue Brain Project circuits."""

    animal = Field.Optional(
        __name__="animal",
        __type__=str,
        __doc__="Animal model that the data was measured for.")

    spatial_parameters = Field(
        __name__="spatial_parameters",
        __type__=set,
        __is_valid__=Field.typecheck.collection(BrainCircuitSpatialParameter),
        __doc__="""A composition phenomenon must be measured as a function of
        location in the brain. Field spatial_parameters can be used to 
        communicate the required measurement parameters to the author of a
        model adapter.""",
        __examples__=[{CorticalLayer()}])

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Which brain region is this BlueBrainCircuitCompositionData for?")

    phenomenon = Field(
        __name__="phenomenon",
        __type__=Phenomenon,
        __doc__="The phenomenon that this data represents.")

    def __init__(self, data, *args, **kwargs):
        """..."""
        #kwargs["data"] = data
        super().__init__(data, *args, **kwargs)

    @abstractmethod
    def get_reference_datasets(self, data_location):
        """..."""
        raise NotImplementedError(
            "Implement get_reference_datasets for your concrete implementation.")

    def _load_from_object(self, data, *args, **kwargs):
        """..."""
        try:
            return (data.datasets, data.primary)
        except AttributeError as e:
            raise TypeError(
                "Expected a 'Record' with fields 'datasets' and 'primary'\n"
                "\t\t Caught AttributeError {}\n".format(e))

    def _load_from_location(self, data_location):
        """Load data from a location
        We provide a default implementation that makes a trivial check.
        The concrete implementation needs to complete this implementation only
        if data will be loaded from a location.
        """
        if not self._is_location(data_location):
            self.logger.alert(
                self.logger.get_source_info(),
                "Cannot load data from argument 'data_location' {}"
                .format(data_location))
            return None

        self.logger.alert(
            self.logger.get_source_info(),
            "Load data from location {}.".format(data_location))
        return self.get_reference_datasets(data_location)

    @property
    def description(self):
        """..."""
        try:
            return self._description
        except AttributeError:
            try:
                return self.primary.what
            except AttributeError as e:
                return "Not Available."
        return None

