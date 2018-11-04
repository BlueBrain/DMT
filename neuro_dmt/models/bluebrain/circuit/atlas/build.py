"""Atlas based circuit build's geometry"""

from abc import abstractmethod
from bluepy.v2.enums import Cell
import numpy as np
from voxcell.nexus.voxelbrain import Atlas
from voxcell.hierarchy import Hierarchy
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.measurement.condition import Condition
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import AtlasRegion
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.specialization\
    import CircuitSpecialization
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid, collect_sample, random_location


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
            region_id
            for region_acronym in self.__get_atlas_region_acronyms(
                    condition)
            for region_id in hierarchy.collect(
                    "acronym", region_acronym, "id")}
        
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

    def get_spanning_column_parameter(self,
            regions=["SSp-ll"]):
        """..."""
        raise NotImplementedError(
            """""")

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
        self._region_geometry = {}
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

    def _get_region_geometry(self,
            condition=Condition([])):
        """Compute geometry of a region."""
        region\
            = condition.get_value(
                Cell.REGION)
        if not region in self._region_geometry:
            region_ids\
                = self.circuit_specialization\
                      .get_atlas_ids(
                          self.hierarchy,
                          condition=Condition([(Cell.REGION, region)]))
            nx, ny, nz\
                    = self.brain_region_voxels.shape
            self.logger.info(
                self.logger.get_source_info(),
                """build is_ids_voxel data of shape {}X{}X{}"""\
                .format(nx, ny, nz))

            region_bottom\
                = np.finfo(float).max
            region_top\
                = np.finfo(float).min

            count = 0 #track iteration
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        pos\
                            = self.brain_region_voxels\
                                  .indices_to_positions(
                                      np.array([i,j,k]) )
                        if self.brain_region_voxels.lookup(pos) in region_ids:
                            if pos[1] > region_top:
                                region_top = pos[1]
                            if pos[1] < region_bottom:
                                region_bottom = pos[1]
                        if count % 1000 == 0:
                            self.logger.info(
                                self.logger.get_source_info(),
                                """check {}-th voxel at position {}"""\
                                .format(count + 1, pos),
                                "\t bottom: {}\t top: {}"\
                                .format(region_bottom, region_top))
                        count += 1
            self._region_geometry[region]\
                = Record(
                    bottom=region_bottom,
                    top=region_top)
        return self._region_geometry[region]

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
            = self.circuit_specialization\
                  .get_atlas_ids(
                      self.hierarchy,
                      condition)
        if self.brain_region_voxels.count(atlas_ids) == 0:
            self.logger.alert(
                self.logger.get_source_info(),
                """Ids for region in condition {} not represented
                in voxel data.""".format(condition.value))
            return None

        count = 0
        while True:
            random_voxel\
                = self.brain_region_voxels\
                      .indices_to_positions(
                          np.array([
                              np.random.randint(n)
                              for n in self.brain_region_voxels.shape]))
            if self.brain_region_voxels.lookup(random_voxel) in atlas_ids:
                return random_voxel
            elif count == 10000000: #10 million. Is that enough?
                self.logger.alert(
                    self.logger.get_source_info(),
                    """10 million voxels sampled, none had ids for the region
                    requested in {}.""".format(condition.value))
                break
            else:
                count += 1
                continue
            break
        return None

    def spanning_column_parameter(self,
            regions=["SSp-ll"],
            *args, **kwargs):
        """Parameter with values that are columns through the
        requiested iso_cortex_regions"""
        return AtlasRegion(
            value_type=str,
            values=regions,
            *args, **kwargs)

    def random_spanning_column(self,
            condition=Condition([(Cell.REGION, "SSp-ll")]),
            crossection=50.):
        """..."""
        region_geometry\
            = self._get_region_geometry(
                condition)
        random_pos\
             = self.random_position(
                 condition)
        random_pos[1] = 0.0
        square\
            = (crossection *
               np.array([
                   1.0, 0.0, 1.0 ]))
        bottom\
            = np.array([
                0.0,
                region_geometry.bottom,
                0.0])
        top\
            = np.array([
                0.0,
                region_geometry.top,
                0.0])
        return Cuboid(
            random_pos - square + bottom,
            random_pos + square + top)

            
               
class CortexAtlasCircuitGeometry(
        AtlasCircuitGeometry):
    """AtlasCircuitGeometry whose 'circuit_specialization' has already
    been set to 'CorticalAtlasSpecialization'"""
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit_specialization\
            = IsoCortexAtlasSpecialization(
                *args, **kwargs)
        super().__init__(
            circuit,
            *args, **kwargs)


