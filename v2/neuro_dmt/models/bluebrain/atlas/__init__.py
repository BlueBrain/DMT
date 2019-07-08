import os
from abc import ABC, abstractmethod
from types import MethodType
import numpy as np
import glob
from warnings import warn
from voxcell.nexus.voxelbrain import Atlas
from voxcell import VoxcellError
# TODO: docstrings, docstrings, docstrings!
# TODO: currently usng two different methods to get available mtypes
# TODO: decouple whethe [cell_density] is filename prefix from whether
#       sclass density is there

BIG_LIST_OF_KNOWN_MTYPES = [
    "RC", "IN", "TC", "BPC", "BP", "BTC", "CHC", "DAC", "DBC", "HAC", "HPC",
    "IPC", "LAC", "LBC", "MC", "NBC", "NGC-DA", "NGC-SA", "NGC", "SAC", "SBC",
    "SSC", "TPC:A", "TPC:B", "TPC:C", "TPC", "UPC"]


def compose_atlas_adapter(atlas_dir):
    """generate an adapter for the atlas provided"""
    adapter = AtlasAdapter(atlas_dir)
    if adapter._atlas.load_region_map().find('L1', 'acronym'):
        adapter._layer_mask = MethodType(LayerMasks.L_number, adapter)
    else:
        adapter._layer_mask = MethodType(LayerMasks.column_semicolon_int,
                                         adapter)
    if has_cell_density(atlas_dir):
        adapter.cell_density = MethodType(CellDensities.has_density,
                                          adapter)
        if has_sclass_densities(atlas_dir):
            adapter._sclass_filename = MethodType(
                CellDensities.SclassFilenames.bracketed_prefix,
                adapter)
            adapter._total_density = MethodType(
                CellDensities.TotalDensities.exc_and_inh,
                adapter)
        else:
            adapter._sclass_filename = MethodType(
                CellDensities.SclassFilenames.has_no_sclass,
                adapter)
            adapter._total_density = MethodType(
                CellDensities.TotalDensities.all_mtypes,
                adapter)

        if has_layer_prefixed_mtypes(atlas_dir):
            adapter._mtype_filename = MethodType(
                CellDensities.MtypeFilenames.layer_prefix,
                adapter)
        else:
            adapter._mtype_filename = MethodType(
                CellDensities.MtypeFilenames.no_prefix,
                adapter)

    else:
        adapter.cell_density = MethodType(CellDensities.no_cell_density,
                                          adapter)

    return adapter


def has_cell_density(atlas_dir):
    return has_sclass_densities(atlas_dir)\
        or has_layer_prefixed_mtypes(atlas_dir)\
        or has_prefixless_mtypes(atlas_dir)


def has_sclass_densities(atlas_dir):
    return len(
        {'[cell_density]EXC.nrrd', '[cell_density]INH.nrrd',
         'EXC.nrrd', 'INH.nrrd'}.intersection(set(os.listdir(atlas_dir)))) > 0


def has_layer_prefixed_mtypes(atlas_dir):
    return any(
        glob.glob(os.path.join(atlas_dir, "*_{}.nrrd".format(mtype)))
        for mtype in BIG_LIST_OF_KNOWN_MTYPES)


def has_prefixless_mtypes(atlas_dir):
    return len(set(mt + ".nrrd" for mt in BIG_LIST_OF_KNOWN_MTYPES)
               .intersection(set(os.listdir(atlas_dir)))) > 0


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
                             for name in
                             _list_if_not_list(self._mtype_filename(mtype))]
            if 'sclass' in query:
                warn(Warning(
                    'mtype keyword overrides sclass in {}.cell_density'
                    .format(self)))

        elif 'sclass' in query:
            density_types = [scname
                             for sclass in _list_if_not_list(query['sclass'])
                             for scname in self._sclass_filename(sclass)]
        else:
            density_types = self._total_density()

        densities = [
            self._atlas.load_data(density_type).raw[mask]
            for density_type in density_types]
        if len(densities) == 0:
            return np.nan
        return np.nansum(densities, axis=0)

    class TotalDensities:

        def exc_and_inh(self):
            return [scname
                    for sclass in ('EXC', 'INH')
                    for scname in self._sclass_filename(sclass)]

        def all_mtypes(self):
            import glob
            from os.path import basename, join
            allnrrdnames = [basename(nrrd).split(".")[0] for nrrd in
                            glob.glob(join(self._atlas.dirpath, "*.nrrd"))]

            mtype_names = [fname for mtype in BIG_LIST_OF_KNOWN_MTYPES
                           for fname in _list_if_not_list(
                                   self._mtype_filename(mtype))]
            all_mtypes = {
                fname for fname in allnrrdnames if fname in mtype_names}

            return list(all_mtypes)

    class SclassFilenames:
        """just a container for _sclass_filename function varieties"""

        def has_no_sclass(self, density_type):
            warn(Warning("{} has no sclass densities".format(self)))
            return []

        def bracketed_prefix(self, density_type):
            # for now assume no UN
            if density_type in ("EXC", "INH"):
                return ['[cell_density]' + density_type]
            else:
                return []

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

        def no_prefix(self, mtype):
            return mtype
