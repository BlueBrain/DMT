"""Atlas based circuit build's geometry"""
import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils import collections
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.brain_regions\
    import BrainRegionSpecific
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry\
    import Cuboid, random_location


class Hippocampal(
        BrainRegionSpecific):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.central_column = "mc2" #for O1 circuits --- can this be generalized?
        super().__init__(
            brain_region=brain_regions.hippocampus,
            *args, **kwargs)

    def atlas_query(self,
            condition,
            *args, **kwargs):
        """..."""
        return {"layer": condition.get_value("layer")}

    def get_atlas_region_acronyms(self,
            condition):
        """In developing this class, we assume that atlas paths will
        follow the convention used in one of Hippocampus O1 circuits:
        brain region's acronym contains the entire hierarchical path,
        with nodes separated by a ';'."""
        layers = condition.get_value("layer")
        if not layers:
            return self.central_column
        if not collections.check(layers):
            return "{};{}".format(self.central_column, layers)
        return [
            "{};{}".format(self.central_column, layer)
            for layer in layers]



class FakeAtlasCircuitGeometry(
        AtlasCircuitGeometry):
    """Specialization of circuit geometry methods for
    (fake) atlas based circuits."""

    specializations = {}

    def __init__(self,
            circuit,
            circuit_specialization,
            *args, **kwargs):
        """...
        Parameters
        -----------------------------------------------------------------------
        BluePy keeps changing in response to circuit building updates,
        and user requests. We delegate the most volatile parts of
        bluepy calls to 'circuit_specialization'. This class should be small,
        and provide only circuit instance specific methods."""
        self._circuit_specialization\
            = circuit_specialization
        super().__init__(
            circuit,
            *args, **kwargs)


    def random_position(self,
            brain_region,
            condition=Record(),
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
        atlas_region_acronyms\
            = self._circuit_specialization\
                  .get_atlas_region_acronyms(
                      condition)
        atlas_ids\
            = self.get_atlas_ids(
                *atlas_region_acronyms)
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

    def column_parameter(self,
            *args, **kwargs):
        """..."""
        raise NotImplementedError("DEVMODE")

    def random_column(self,
            *args, **kwargs):
        """..."""
        raise NotImplementedError("DEVMODE")
