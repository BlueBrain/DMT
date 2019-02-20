"""Circuit data used for building and validating circuits
at the Blue Brain Project."""
import os
from abc\
    import abstractmethod
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.data.reference\
    import MultiReferenceData
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter\
    ,      CorticalLayer\
    ,      BrainCircuitConnectomeParameter
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.data.bluebrain import BlueBrainData

class BlueBrainCircuitData(
        BlueBrainData,
        MultiReferenceData):
    """Base class that describes circuit data used for validating
    Blue Brain Project circuits."""

    __available_data = {}

    animal=\
        Field(
            __name__="animal",
            __type__=str,
            __default__="mammal",
            __doc__="Animal model that the data was measured for.")
    brain_region=\
        Field(
            __name__="brain_region",
            __type__=BrainRegion,
            __doc__="""Which brain region is this
            BlueBrainCircuitCompositionData for?""")
    phenomenon=\
        Field(
            __name__="phenomenon",
            __type__=Phenomenon,
            __doc__="The phenomenon that this data represents.")
    data_location=\
        Field(
            __name__="data_location",
            __type__=dict,
            __typecheck__=Field.typecheck.mapping(str, str),
            __doc__="""data location for a MultiReferenceData should be a
            dict mapping data label to its location.""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """Data is loaded from self.data_location"""
        self.logger.debug(
            self.logger.get_source_info(),
            "initialize {}".format(self.__class__),
            "with phenomenon {}".format(phenomenon),
            "with data_location {}".format(
                kwargs.get(
                    "data_location",
                    "not provided")))
        super().__init__(
            phenomenon=phenomenon,
            *args, **kwargs)
        self.__class__.insert(self)

    @property
    def label(self):
        """This is a default implementation.
        Implement a specification for your needs."""
        return self.phenomenon.label

    def get_reference_datasets(self,
            data_location):
        """..."""
        raise NotImplementedError(
            """Implement get_reference_datasets
            for your concrete implementation.""")

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

    @abstractmethod
    def get(self,
            phenomenon,
            *args, **kwargs):
        """Get data for a given phenomenon."""
        return NotImplementedError("Implement this method.")


class BlueBrainCircuitCompositionData(
        BlueBrainCircuitData):
    """Base class that describes circuit composition data used for validating
     Blue Brain Project circuits."""

    spatial_parameters=\
        Field(
            __name__ = "spatial_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitSpatialParameter),
            __doc__ = """A composition phenomenon must be measured as 
            a function of location in the brain. Field spatial_parameters 
            can be used to communicate the required measurement parameters
            to the author of a model adapter.""",
            __examples__ = [[CorticalLayer()]])
    pass

class BlueBrainCircuitConnectomeData(
        BlueBrainCircuitData):
    """Base class that describes circuit connectome data used for validating
    Blue Brain Project circuits."""

    pathway_parameters=\
        Field(
            __name__ = "pathway_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a function
            of either the cell type or a pair of cell types (defining the
            pathway) Fields pathway_parameters and cell_group_parameters
            can be used to communicate the required measurement parameters
            to the author of a model / data adapter.""",
            __examples__= [
                [Mtype(label="pre_mtype"), Mtype(label="post_mtype")]])
    cell_group_parameters=\
        Field(
            __name__ = "cell_group_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a function
            of either the cell type or a pair of cell types (defining the
            pathway) Fields pathway_parameters and cell_group_parameters
            can be used to communicate the required measurement parameters
            to the author of a model / data adapter.""",
            __examples__= [Mtype()])
                
