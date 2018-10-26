"""Atlas based circuit build's geometry"""

from abc import abstractmethod
from voxcell.nexus.voxelbrain import Atlas
from voxcell.hierarchy import Hierarchy
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry


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

    def get_atlas_ids(self,
            *regions):
        """We can get region ids from the atlas, one region at a time,
        but may want region ids for several regions at the same time."""
        return {
            id for region in regions
            for id in self.hierarchy.collect(
                    "acronym", region, "id")}
