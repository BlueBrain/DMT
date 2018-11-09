"""Atlas based circuit build's geometry"""
from abc\
    import abstractmethod
import numpy\
    as np
from bluepy.v2.enums\
    import Cell
from dmt.vtk.utils\
    import collections
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import Column
from neuro_dmt.models.bluebrain.circuit.O1.build import \
    O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.build import\
    AtlasBasedLayeredCircuitSpecialization,\
    AtlasBasedCircuitSpecialization,\
    AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry\
    import Cuboid, random_location


class FakeAtlasCircuitGeometry(
        AtlasCircuitGeometry,
        O1CircuitGeometry):
    """Circuit geometry methods for (fake) atlas based circuits."""

    label = "O1Atlas"

    def __init__(self,
            circuit,
            *args, **kwargs):
        """...
        Parameters
        -----------------------------------------------------------------------
        BluePy keeps changing in response to circuit building updates,
        and user requests. We delegate the most volatile parts of
        bluepy calls to 'circuit_specialization'. This class should be small,
        and provide only circuit instance specific methods."""
        self.__layer_geometry = None
        super().__init__(
            circuit,
            *args, **kwargs)

    def spanning_column_parameter(self,
            regions=[2], #these should be O1 meso-columns
            *args, **kwargs):
        """..."""
        return\
            self.circuit_specialization\
                .get_spanning_column_parameter(
                    regions)

    def __compute_geometry(self):
        """..."""
        self.logger.info(
            self.logger.get_source_info(),
            """Compute geometry in {} instance"""\
            .format(self.__class__.__name__))
        central_column_ids\
            = self.circuit_specialization\
                  .get_atlas_ids(
                      self.hierarchy)
        self.logger.info(
            self.logger.get_source_info(),
            """central column region ids in atlas {}""".format(
                central_column_ids))
        is_ids_voxel\
            = self.brain_region_voxels.with_data(
                np.in1d(
                    self.brain_region_voxels.raw,
                    list(central_column_ids)
                ).reshape(
                    self.brain_region_voxels.shape))
        nx, ny, nz\
            = self.brain_region_voxels\
                  .shape
        self.logger.info(
            self.logger.get_source_info(),
            "brain_region shape: {}".format(
                self.brain_region_voxels.shape))
        voxels\
            = self.brain_region_voxels\
                  .indices_to_positions(
                      np.array([
                          np.array([i,j,k])
                          for i in range(nx)
                          for j in range(ny)
                          for k in range(nz)]))
        self.logger.info(
            self.logger.get_source_info(),
            "voxels shape: {}".format(
                voxels.shape))
        central_column_voxels\
            = np.array([
                v for v in voxels
                if is_ids_voxel.lookup(v)])
                #if self.brain_region_voxels.lookup(v) in central_column_ids])
        self.logger.info(
            self.logger.get_source_info(),
            "central_column_voxels shape: {}".format(
            central_column_voxels.shape))
        self.__layer_geometry\
            = Record(
                column_bottom=np.min(
                    central_column_voxels[:, 1]),
                column_top=np.max(
                    central_column_voxels[:, 1]))
        self.logger.info(
            self.logger.get_source_info(),
            "layer geometry computed {}".format(
                self.__layer_geometry))

    def random_spanning_column(self,
            condition=Condition([]),
            crossection=50.):
        """..."""
        if not self.__layer_geometry:
            self.__compute_geometry()
        random_pos\
            = self.random_position(condition)
        random_pos[1] = 0.0 
        square\
            = (crossection *
               np.array([
                   1.0, 0.0, 1.0 ]))
        bottom\
            = np.array([
                0.0,
                self.__layer_geometry.column_bottom,
                0.0 ])
        top\
            = np.array([
                0.0,
                self.__layer_geometry.column_top,
                0.0])
        return Cuboid(
            random_pos - square + bottom,
            random_pos + square + top)


