"""Atlas based circuit build's geometry"""

from abc import abstractmethod
import numpy as np
from voxcell.nexus.voxelbrain import Atlas
from voxcell.hierarchy import Hierarchy
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.condition import Condition
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.utils import brain_regions


class AtlasCircuitGeometry(
        CircuitGeometry):
    """Specify atlas circuit based attributes."""

    atlas\
        = Field(
            __name__="atlas",
            __type__=Atlas,
            __doc__="""Brain atlas used to build this circuit.""")

    def __init__(self,
            circuit,
            circuit_specialization,
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
        self.label = "Atlas"
        self._hierarchy = None
        self._brain_region_voxels = None
        self._circuit_specialization\
            = circuit_specialization
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
            brain_region=brain_regions.whole_brain,
            condition=Condition([]),
            offset=50.*np.ones(3)):
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
            = self._circuit_specialization.get_atlas_ids(
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

