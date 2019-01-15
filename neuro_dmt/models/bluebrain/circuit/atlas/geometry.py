"""Parameters relevant for an atlas based circuit."""
import numpy as np
from voxcell import VoxelData
from voxcell.nexus.voxelbrain\
    import Atlas
from dmt.vtk.utils.descriptor\
    import Field, WithFCA
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter

class CorticalColumn(
        WithFCA):
    """Provides a column like object in a brain region."""
    atlas=\
        Field(
            __name__="atlas",
            __type__=Atlas,
            __doc__="""The brain atlas in which cortical columns will be
            provided.""")
    voxel_size=\
        Field(
            __name__="voxel_size",
            __type__=float,
            __doc__="Size of a voxel in the atlas.")
    region=\
        Field(
            __name__="region",
            __typecheck__=Field.typecheck.any(
                str,
                VoxelData,
                np.ndarray),
            __doc__="""Brain region acronym for which to create
            this cortical column.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        self._hierarchy=\
            None
        self._region_mask=\
            None
        self._voxel_cortical_depth=\
            None
        self._depths=\
            None
        self._voxel_ids=\
            {}
        self._bottom=\
            np.nan
        self._top=\
            np.nan
        super().__init__(
            *args, **kwargs)

    @property
    def hierarchy(self):
        """..."""
        if not self._hierarchy:
            self._hierarchy=\
                self.atlas.load_hierarchy()
        return self._hierarchy

    @property
    def region_mask(self):
        """..."""
        if not self._region_mask:
            if isinstance(self.region, str):
                self._region_mask=\
                    self.atlas.get_region_mask(
                        self.region
                    ).raw
            if isinstance(self.region, np.ndarray):
                self._region_mask=\
                    self.region
            if isinstance(self.region, VoxelData):
                self._region_mask=\
                    self.region.raw
        return self._region_mask

    @property
    def voxel_cortical_depth(self):
        """..."""
        if self._voxel_cortical_depth is None:
            self._voxel_cortical_depth=\
                self.atlas.load_data(
                    "[PH]y").raw + self.voxel_size / 2.
            self._voxel_cortical_depth[np.logical_not(self.region_mask)]=\
                np.nan
        return self._voxel_cortical_depth

    @property
    def top(self):
        """..."""
        if np.isnan(self._top):
            self._top=\
                np.nanmax(
                    self.voxel_cortical_depth)
        return self._top

    @property
    def bottom(self):
        """..."""
        if np.isnan(self._bottom):
            self._bottom=\
                np.nanmin(
                    self.voxel_cortical_depth)
        return self._bottom

    # def _set_voxel_ids(self):
    #     """Set voxel ids..."""
    #     self.logger.info(
    #         self.logger.get_source_info(),
    #         """Setting CorticalColumn {} voxel ids by depth""".format(self.region))
    #     depths=\
    #         np.unique(
    #             self.voxel_cortical_depth)
    #     self._depths=\
    #         depths[np.logical_not(np.isnan(depths))]
    #     self.logger.info(
    #         self.logger.get_source_info(),
    #         """Unique depths in the region: {}""".format(self._depths))
    #     self._voxel_ids=\
    #         {depth: list(zip(
    #             *np.nonzero(
    #                 self.voxel_cortical_depth == depth)))
    #          for depth in depths}
    #     self.logger.info(
    #         self.logger.get_source_info(),
    #         "Done")

    @property
    def depths(self):
        """Unique voxel depths """
        if self._depths is None:
            depths=\
                np.unique(
                    self.voxel_cortical_depth)
            self._depths=\
                depths[
                    np.logical_not(
                        np.isnan(depths))]
        return self._depths

    def get_voxel_ids(self,
            depth):
        """A dict mapping depth to voxel ids at that depth."""
        self.logger.info(
            self.logger.get_source_info(),
            """Get voxel ids at (binned) depth {}""".format(depth))
        if not depth in self.depths:
            raise ValueError(
                """Queried depth {} not a value in
                CorticalColumn voxel depths {}""".format(
                    depth,
                    self._depths))
        if not depth in self._voxel_ids:
            self._voxel_ids[depth]=\
                list(zip(
                    *np.nonzero(
                        self.voxel_cortical_depth == depth)))
        vids=\
            self._voxel_ids[depth]
        self.logger.info(
            self.logger.get_source_info(),
            """found {} voxels""".format(len(vids)))
        return vids

    # def get_voxel_ids(self,
    #         depth):
    #     """A dict mapping depth to voxel ids at that depth."""
    #     if not self._voxel_ids:
    #         self._set_voxel_ids()
    #     return self._voxel_ids[depth]

    def get_random_voxel(self,
            depth_fraction):
        """Get a random voxel at a given depth fraction."""
        depth=\
            self.top - depth_fraction * (self.top - self.bottom)
        self.logger.debug(
            self.logger.get_source_info(),
            """Get random voxel containing depth fraction {} (at depth {})"""\
            .format(
                depth_fraction,
                depth))
        try: 
            index=\
                np.argwhere(
                    np.logical_and(
                        depth >= self.depths - self.voxel_size / 2.,
                        depth <  self.depths + self.voxel_size / 2.))[0][0]
        except IndexError as ierr:
            self.logger.alert(
                self.logger.get_source_info(),
            """queried depth fraction {} (amounting to a depth of {}) does not
            bin to any of the voxel depths in {}""".format(
                depth_fraction,
                depth,
                self.depths))
            return None

        candidates=\
            self.get_voxel_ids(
                self.depths[index])
        if len(candidates) == 0:
            return none

        return candidates[
            np.random.randint(len(candidates))]
