from abc import ABC, abstractmethod
from types import MethodType
import numpy as np
from warnings import warn
from voxcell.nexus.voxelbrain import Atlas
from voxcell import VoxcellError
# TODO: docstrings, docstrings, docstrings!


def compose_atlas_adapter(atlas_dir):
    """generate an adapter for the atlas provided"""
    adapter = AtlasAdapter(atlas_dir)
    if adapter._atlas.load_region_map().find('L1', 'acronym'):
        adapter._layer_mask = MethodType(LayerMasks.L_number, adapter)
    else:
        adapter._layer_mask = MethodType(LayerMasks.column_semicolon_int,
                                         adapter)
    try:
        adapter._atlas.load_data("[cell_density]EXC")
        adapter.cell_density = MethodType(CellDensities.has_density,
                                          adapter)
        adapter._sclass_filename = MethodType(
            CellDensities.SclassFilenames.bracketed_prefix,
            adapter)
        adapter._mtype_filename = MethodType(
            CellDensities.MtypeFilenames.layer_prefix,
            adapter)
    except VoxcellError:
        adapter.cell_density = MethodType(CellDensities.no_cell_density,
                                          adapter)

    return adapter


def _list_if_not_list(item):
    if isinstance(item, list):
        return item
    return [item]


# TODO: what if someone wants to request a property for
#       region X OR layer Y
#       OPTION1: accept list of queries and interperet as or
#       OPTION2: create query class and allow constructing
#               from other queries with and/or
#       pref. option 1 for now
# TODO: what if someone wants to exclude from their query
#       e.g. All Thalamus except RT
#       OPTION1: option 2 above, including 'not'
#       OPTION2: allow 'exclude' key in query, which links to
#                another query of values to exclude
class AtlasAdapter(ABC):

    def __init__(self, atlas):
        if isinstance(atlas, Atlas):
            self._atlas = atlas
        else:
            self._atlas = Atlas.open(atlas)

    # TODO: should I pass whole query to _translate_layer
    def mask_for_query(self, query):
        masks = [self._atlas.load_data("brain_regions").raw > 0]
        if 'region' in query:
            region_mask = np.any(
                [self._region_mask(region)
                 for region in _list_if_not_list(query['region'])], axis=0)
            masks.append(region_mask)
        if 'layer' in query:
            layer_mask = np.any(
                [self._layer_mask(layer)
                 for layer in _list_if_not_list(query['layer'])], axis=0)
            masks.append(layer_mask)
        if 'column' in query:
            column_mask = np.any(
                [self._column_mask(column)
                 for column in _list_if_not_list(query['column'])], axis=0)
            masks.append(column_mask)

        return np.all(masks, axis=0)

    # TODO: compose

    def _region_mask(self, region):
        warn(Warning("{} ignores 'region' as it is not relevant to O1 atlas"
                     .format(self)))
        return self._atlas.load_data("brain_regions").raw != 0

    def _column_mask(self, column):
        return self._atlas.get_region_mask(column + "_Column").raw


    # # TODO: compose
    # def _density_types(self):
    #     import glob
    #     import os
    #     all_nrrds = glob.glob(os.path.join(self._atlas.dirpath, "*.nrrd"))
    #     all_nrrds = [os.path.basename(nrrd).split(".")[0] for nrrd in all_nrrds]
    #     all_nrrds = [nrrd.split("[cell_density]")[1] if nrrd.startswith("[cell_density]") else nrrd
    #                 for nrrd in all_nrrds]
    #     excluded = ['brain_regions', 'orientation', '[PH]y', 'height', 'distance', 'relative_distance', 'depth'] \
    #     + ['[PH]{}'.format(i) for i in range(1, 7)]\
    #     + ['thickness:L{}'.format(i) for i in range(1, 7)]\
    #     + ["EXC", "INH"]

    #     density_nrrds = [nrrd for nrrd in all_nrrds if nrrd not in excluded]
    #     return density_nrrds

    #     return sum(
    #         self._atlas.load_data(self._cell_sclass_filename(dtype)).raw[mask]
    #         for dtype in sclass)#density_types)


# TODO: instead of functions I could use callable classes  which inherit from
#       a superclass


class LayerMasks:
    """just a container for _layer_mask function varieties"""

    def column_semicolon_int(self, layer):
        return self._atlas.get_region_mask(
            "@;{}$".format(layer[1]), attr="acronym").raw

    def L_number(self, layer):
        # TODO: auto-detect on initialization?
        return self._atlas.get_region_mask(
            "@{}$".format(layer), attr="acronym").raw


# TODO: certain functions here are dependent on other methods being assigned
#       e.g. _mtype_filename , _sclass_filename
#       (how) do I enforce this?
class CellDensities:
    """just a container for cell_density function varieties"""
    def no_cell_density(self, query):
        warn(Warning("{} atlas has no cell density, returning NaN"
                     .format(self)))
        return np.nan

    def has_density(self, query):
        mask = self.mask_for_query(query)
        if 'mtype' in query:
            density_types = [name
                             for mtype in _list_if_not_list(query['mtype'])
                             for name in self._mtype_filename(mtype)]
            if 'sclass' in query:
                warn(Warning(
                    'mtype keyword overrides sclass in {}.cell_density'
                    .format(self)))

        elif 'sclass' in query:
            density_types = [self._sclass_filename(sclass)
                             for sclass in _list_if_not_list(query['sclass'])]
        else:
            density_types = [self._sclass_filename(sclass)
                             for sclass in ('EXC', 'INH')]
        return np.nansum([
            self._atlas.load_data(density_type).raw[mask]
            for density_type in density_types], axis=0)

    class SclassFilenames:
        """just a container for _sclass_filename function varieties"""

        def bracketed_prefix(self, density_type):
            return '[cell_density]' + density_type

    class MtypeFilenames:
        """just a container for _mtype_filename function varieties"""

        def layer_prefix(self, mtype):
            from glob import glob
            from os.path import join, basename
            allnames = glob(
                join(self._atlas.dirpath, "*_" + mtype + ".nrrd"))
            basenames = [basename(name).split(".")[0]
                         for name in allnames]
            return basenames
