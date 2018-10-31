"""Atlas based circuit build's geometry"""

from abc import abstractmethod
from bluepy.v2.enums import Cell
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


class AtlasBasedCircuitSpecialization(
        CircuitSpecialization):
    """Base class for atlas based circuit specializations."""

        
    @abstractmethod
    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """..."""
        pass


class AtlasBasedLayeredCircuitSpecialization(
        AtlasBasedCircuitSpecialization):
    """'get_atlas_ids method defined here seems to be the future of
    atlas based circuits that have layers. All such circuits must inherit this
    class so that we can update future (of 20181039) changes.
    We design these class so that the code here can be used even for fake
    atlas O1 circuits."""

    atlas_acronym_separator\
        = Field(
            __name__="atlas_acronym_separator",
            __type__=str,
            __doc__="""Separates region label from that of the layers. Should
            work for cortical and hippocampal regional circuits.""")

    representative_region\
        = Field(
            __name__="representative_region",
            __type__=str,
            __doc__="""Out of all (sub) regions modeled in the brain-circuit,
            which one is representative. Provide its acronym.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

    def __get_atlas_region_acronyms(self,
            condition):
        """We assume that the atlas paths will continue to follow conventions
        assumed here. Currently (20181030) we have observed these conventions
        in a Hippocampus circuit from 201809DD and the iso-cortex
        (under-development) atlas."""
        layers\
            = condition.get_value(
                Cell.LAYER)
        region\
            = condition.get_value(
                Cell.REGION)
        if not region:
            region\
                = self.representative_region
        if not layers:
            return [region]
        if not collections.check(layers):
            return [
                "{}{}{}".format(
                    region,
                    self.atlas_acronym_separator,
                    layers)]
        return [
            "{}{}{}".format(
                region,
                self.atlas_acronym_separator,
                layer)
            for layer in layers]

    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """..."""
        return {
            id for region in self.__get_atlas_region_acronyms(condition)
            for id in hierarchy.collect(
                    "acronym", region, "id")}
        
    @property
    def target(self):
        """..."""
        return self.representative_region


class IsoCortexAtlasSpecialization(
        AtlasBasedLayeredCircuitSpecialization):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        if "brain_region" not in kwargs: #if there, it should be a cortex sub-region, eg SSCx
            kwargs["brain_region"]\
                = brain_regions.cortex
        self.atlas_acronym_separator\
            = '' #empty string, i.e. no separator
        self.representative_region\
            = "SSp-ll" #primary Somatosensory lower-limb (i.e. hind-limb)
        super().__init__(
            *args, **kwargs)

    def get_atlas_ids(self,
            hierarchy,
            condition=Condition([])):
        """..."""
        layers\
            = condition.get_value(
                "layer")
        isocortex_region\
            = condition.get_value(
                Cell.REGION) 
        if not layers:
            return hierarchy.collect(
                "acronym", isocortex_region,  "id")
        if not collections.check(layers):
            return hierarchy.collect(
                "acronym", isocortex_region, "id"
            ).intersection(
                hierarchy.collect(
                    "acronym", "L{}".format(layers), "id"))
        return hierarchy.collect(
                "acronym", isocortex_region, "id"
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
        self.logger.info(
            self.logger.get_source_info(),
            """Get random position from atlas based circuit geometry's.""",
            """\tgiven: {}""".format(condition.value))
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

    def random_spanning_column(self,
            region,
            *args, **kwargs):
        """A random column (a long box) passing through all the 6 layers,
        contained (mostly) inside the requested (sub) region of the circuit."""
        raise NotImplementedError(
            "A column that spans all the layers of a (sub) region of the circuit.")

    def spanning_column_parameter(self,
            regions=[],
            *args, **kwargs):
        """Parameter with values that are columns through the
        requiested iso_cortex_regions"""
        raise NotImplementedError
