"""Atlas based circuit build's geometry"""

from abc import abstractmethod
import numpy as np
from voxcell.nexus.voxelbrain import Atlas
from voxcell.hierarchy import Hierarchy
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils import collections
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.condition import Condition
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.specialization\
    import CircuitSpecialization
from neuro_dmt.utils import brain_regions


class AtlasCircuitSpecialization(
        CircuitSpecialization):
    """Base class for atlas based circuit specializations."""

    @abstractmethod
    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """..."""
        pass

class IsoCortexAtlasSpecialization(
        AtlasCircuitSpecialization):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.column_parameter\
            = Column(
                value_type=str,
                values=["mc{}_Column".format(n) for n in range(7)])
        if "brain_region" not in kwargs: #if there, it should be a cortex sub-region, eg SSCx
            kwargs["brain_region"]\
                = brain_regions.cortex
        super().__init__(
            *args, **kwargs)

    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """..."""
        layers\
            = condition.get_value(
                "layer")
        subregion\
            = condition.get_value(
                "subregion") #subregion of the iso-cortex
        if not layers:
            return hierarchy.collect(
                "acronym", subregion,  "id")
        if not collections.check(layers):
            return hierarchy.collect(
                "acronym", subregion, "id"
            ).intersection(
                hierarchy.collect(
                    "acronym", "L{}".format(layers), "id"))
        return hierarchy.collect(
                "acronym", subregion, "id"
            ).intersection({
                id for layer in layers
                for id in hierarchy.collect(
                        "acronym", "L{}".format(layer), "id")})
        
    @property
    def target(self):
        """..."""
        raise NotImplementedError
 
class AtlasCircuitGeometry(
        CircuitGeometry):
    """Specify atlas circuit based attributes."""
    label = "Atlas"

    atlas\
        = Field(
            __name__="atlas",
            __type__=Atlas,
            __doc__="""Brain atlas used to build this circuit.""")
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        if "atlas" not in kwargs:
            try:
                kwargs["atlas"] = circuit.atlas
            except AttributeError as e:
                raise AttributeError(
                    """Atlas neither passed as a key-word argument,
                    nor available as a circuit instance {}'s attribute."""\
                    .format(self))
        self._hierarchy = None
        self._brain_region_voxels = None
        super().__init__(
            circuit,
            *args, **kwargs)


    @property
    def hierarchy(self):
        """Hierarchy of brain regions in the atlas."""
        if not self._hierarchy:
            self._hierarchy = self.atlas.load_hierarchy()
        return self._hierarchy

    @property
    def brain_region_voxels(self):
        """..."""
        if not self._brain_region_voxels:
            self._brain_region_voxels\
                = self.atlas.load_data(
                    "brain_regions")
        return self._brain_region_voxels


    def random_position(self,
            condition=Condition([]),
            offset=50.*np.ones(3),
            *args, **kwargs):
        """Get a random position in region given by "brain_region" under given
        'condition'. The parameter 'condition' will subset a region inside
        'brain_region'.
        Parameters
        -----------------------------------------------------------------------
        brain_region:
        ~    The larger brain region that the circuit was built for.
        ~    Examples: SSCx, hippocampus CA1, Iso-cortex
        condition:
        ~    specifies a region inside brain_region to get a random position in
        """
        atlas_ids\
            = self.circuit_specialization.get_atlas_ids(
                self.hierarchy,
                condition)
        is_ids_voxel\
            = self.brain_region_voxels.with_data(
                np.in1d(
                    self.brain_region_voxels.raw,
                    list(atlas_ids)
                ).reshape(
                    self.brain_region_voxels.shape))
        while True:
            random_voxel\
                = self.brain_region_voxels\
                      .indices_to_positions(
                          np.array([
                              np.random.randint(n)
                              for n in self.brain_region_voxels.shape]))
            if is_ids_voxel.lookup(random_voxel):
                return random_voxel
            else:
                continue
            break
        return None

    def random_column(self,
            iso_cortex_subregion,
            *args, **kwargs):
        """..."""
        raise NotImplementedError(
            "random_column that spans all the layers of an Isocortex subregion.")

    def column_parameter(self,
            iso_cortex_subregion,
            *args, **kwargs):
        """..."""
        raise NotImplementedError
