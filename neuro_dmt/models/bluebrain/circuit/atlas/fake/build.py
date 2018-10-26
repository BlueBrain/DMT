"""Atlas based circuit build's geometry"""
import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils import collections
from dmt.vtk.measurement.condition import Condition
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

    def get_atlas_region_acronyms(self,
            condition):
        """In developing this class, we assume that atlas paths will
        follow the convention used in one of Hippocampus O1 circuits:
        brain region's acronym contains the entire hierarchical path,
        with nodes separated by a ';'."""
        layers = condition.get_value("layer")
        if not layers:
            return [self.central_column]
        if not collections.check(layers):
            return [
                "{};{}".format(self.central_column, layers)]
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
        self.__thickness\
            = None
        self.__column_top\
            = None
        self.__column_bottom\
            = None
        super().__init__(
            circuit,
            circuit_specialization,
            *args, **kwargs)

    def column_parameter(self,
            *args, **kwargs):
        """..."""
        raise NotImplementedError("DEVMODE")

    def __compute_geometry(self):
        """..."""
        central_column_ids\
            = self.get_atlas_ids(
                self._circuit_specialization.central_column)
        is_ids_voxel\
            = self.brain_region_voxels.with_data(
                np.in1d(
                    self.brain_region_voxels.raw,
                    list(central_column_ids)
                ).reshape(
                    self.brain_region_voxels.shape))
        nx, ny, nz = self.brain_region_voxels.shape
        voxels\
            = self.brain_region_voxels\
                  .indices_to_positions(
                      np.array([
                          np.array([i,j,k])
                          for i in range(nx)
                          for j in range(ny)
                          for k in range(nz)]))
        self.central_column_voxels\
            = np.array([
                v for v in voxels
                if self.brain_region_voxels.lookup(v) in central_column_ids])
                #if is_ids_voxel.lookup(voxel)])
        self.__column_bottom\
            = np.min(self.central_column_voxels[:, 1])
        self.__column_top\
            = np.max(self.central_column_voxels[:, 1])
        self.__thickness\
            = self.__column_top - self.__column_bottom

    @property
    def thickness(self):
        """..."""
        if self.__thickness is None:
            self.__compute_geometry()
        return self.__thickness

    @property
    def column_bottom(self):
        """..."""
        if self.__column_bottom is None:
            self.__compute_geometry()
        return self.__column_bottom

    @property
    def column_top(self):
        """..."""
        if self.__column_top is None:
            self.__compute_geometry()
        return self.__column_top

    def random_column(self,
            brain_region=brain_regions.whole_brain,
            crossection=50.):
        """..."""
        random_pos\
            = self.random_position()
        random_pos[1] = 0.0 
        square\
            = (crossection *
               np.array([
                   1.0, 0.0, 1.0 ]))
        bottom\
            = np.array([
                0.0,
                self.column_bottom,
                0.0 ])
        top\
            = np.array([
                0.0,
                self.column_top,
                0.0])
        return Cuboid(
            random_pos - square + bottom,
            random_pos + square + top)
