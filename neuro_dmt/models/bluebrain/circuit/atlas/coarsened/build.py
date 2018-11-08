"""Circuit geometry in which we use coarse grained voxelization."""

import numpy as np
from voxcell import VoxelData
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasBasedCircuitSpecialization, AtlasCircuitGeometry


class CoarseGrainedAtlasCircuitGeometry(
        AtlasCircuitGeometry):
    """..."""
    """Specify atlas circuit based attributes,
    and methods to coarse grain its voxelization."""

    coarse_graining_factor\
        = Field(
            __name__="coarse_graining_factor",
            __type__=int,
            __doc__="""Factor with which to coarse grain atlas voxelization.
            The original atlas voxelization may not be appropriate to
            measure spatial properties. If we coarse grain an atlas'
            voxelization, we can directly sample the voxels instead of picking
            a position and then constructing a Cuboid around it.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

    @staticmethod
    def __majority_item(
            item_array,
            post_process=int):
        """find the majority item in an array of ids.
        Post-process to return an int by default
        (method will be used to process region ids in an atlas.)"""
        unique_counts\
            = np.unique(
                    item_array,
                    return_counts=True)
        return\
            post_process(
                unique_counts[0][
                    np.argmax(unique_counts[1])])

    def __coarse_grained(self,
            voxel_data=None,
            factor=None,
            aggregate=np.nanmean):
        """..."""
        if not voxel_data:
            voxel_data\
                = self.atlas.load_data(
                    "brain_regions")
        if not factor:
            factor\
                = self.coarse_graining_factor
        new_dimension\
            = factor * voxel_data.voxel_dimensions
        data_dimension\
            = voxel_data.raw.shape[voxel_data.ndim:]
        new_shape\
            = tuple(1 + np.array(voxel_data.shape) // factor) + data_dimension
        raw_coarse_grained\
            = np.zeros(shape=new_shape)
        for i in range(new_shape[0]):
            for j in range(new_shape[1]):
                for k in range(new_shape[2]):
                    raw_coarse_grained[i, j, k]\
                        = aggregate(
                            voxel_data.raw[
                                factor * i : factor * (i + 1),
                                factor * j : factor * (j + 1),
                                factor * k : factor * (k + 1)] )
        return\
            VoxelData(
                raw_coarse_grained,
                new_dimension,
                voxel_data.offset)


    @property
    def brain_region_voxels(self):
        """..."""
        if not self._brain_region_voxels:
            self._brain_region_voxels\
                = self.__coarse_grained(
                    voxel_data=self.atlas.load_data(
                        "brain_regions"),
                    aggregate=self.__majority_item)

        return self._brain_region_voxels
