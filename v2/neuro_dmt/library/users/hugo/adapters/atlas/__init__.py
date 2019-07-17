import os
import numpy as np
import glob
from warnings import warn
from voxcell.nexus.voxelbrain import Atlas
# TODO: currently usng two different methods to get available mtypes, choose
# TODO: decouple whethe [cell_density] is filename prefix from whether
#       sclass density is there
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
BIG_LIST_OF_KNOWN_MTYPES = [
    "RC", "IN", "TC", "BPC", "BP", "BTC", "CHC", "DAC", "DBC", "HAC", "HPC",
    "IPC", "LAC", "LBC", "MC", "NBC", "NGC-DA", "NGC-SA", "NGC", "SAC", "SBC",
    "SSC", "TPC:A", "TPC:B", "TPC:C", "TPC", "UPC"]


def is_O1_atlas(atlas):
    return len(atlas.load_region_map().find("O1 mosaic", "name")) > 0


def has_cell_density(atlas):
    """checks for any cell density data"""
    return has_sclass_densities(atlas)\
        or has_layer_prefixed_mtypes(atlas)\
        or has_prefixless_mtypes(atlas)


def has_sclass_densities(atlas):
    """checks for sclass-specific density"""
    atlas_dir = atlas.dirpath
    return len(
        {'[cell_density]EXC.nrrd', '[cell_density]INH.nrrd',
         'EXC.nrrd', 'INH.nrrd'}.intersection(set(os.listdir(atlas_dir)))) > 0


def has_layer_prefixed_mtypes(atlas):
    """checks whether mtype densities with
       layer prefixes are present in the atlas"""
    atlas_dir = atlas.dirpath
    return any(
        glob.glob(os.path.join(atlas_dir, "*_{}.nrrd".format(mtype)))
        for mtype in BIG_LIST_OF_KNOWN_MTYPES)


def has_prefixless_mtypes(atlas):
    """checks whether mtype densities without layer prefix
    are present in the atlas"""
    atlas_dir = atlas.dirpath
    return len(set(mt + ".nrrd" for mt in BIG_LIST_OF_KNOWN_MTYPES)
               .intersection(set(os.listdir(atlas_dir)))) > 0


def is_paxinos_watson(atlas):
    """
    checks if region acronyms corresponding to paxinos-watson based
    somatosensory atlas are present. returns True if they are
    """
    rmap = atlas.load_region_map()
    if rmap.find("SSCtx", "acronym") or rmap.find("S1HL", 'acronym'):
        return True
    return False


def _list_if_not_list(item):
    """make something a list if it isn't"""
    if isinstance(item, list):
        return item
    return [item]


# TODO: perhaps adapter configuration should be something you can
#       pass to the adapter, to bypass automatic configuration?
#       this lets you manually specify traits when inference doesn't work
#       OPTION: abstract property inference to an AtlasSpec
# TODO: make atlas properties accessible from upper level, perhaps
#       follow if-inside branch approach, and infer beforehand
#       then we send subobjects the AtlasAdapter instance
#       so that they do not need to repeat the tests
class AtlasAdapter():
    """adapter for a wide set of atlases"""

    def __init__(self, atlas):
        """initialize the adapter for the atlas"""
        if isinstance(atlas, Atlas):
            self._atlas = atlas
        else:
            self._atlas = Atlas.open(atlas)
        self._mask_generator = _MaskGenerator(self._atlas)
        self._cell_density_generator = _CellDensityGenerator(self._atlas)

    def mask_for_query(self, query):
        """get a mask corresponding to query"""
        # delegate
        return self._mask_generator(query)

    def cell_density(self, query):
        """get atlas cell density"""
        density_volume = self._cell_density_generator(query)
        if np.all(np.isnan(density_volume)):
            return np.nan
        return density_volume[self.mask_for_query(query)]


class _MaskGenerator:
    """helper class for AtlasAdapter, handles getting the mask for a query"""

    def __init__(self, atlas):
        self._atlas = atlas
        self._layer_mask = _LayerMask(atlas)
        self._region_mask = _RegionMask(atlas)
        self._column_mask = _ColumnMask(atlas)

    def __call__(self, query):
        """get the mask for query"""
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


class _MutateCall:
    """
    base class for dynamically composed callables
    implement the _method method,
    and it will be used when the instance is called
    """

    def _method(self, q):
        """the method to execute on call"""
        # cannot be abstract, as is only assigned after initialization
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """forward to self._method"""
        return self._method(*args, **kwargs)


class _LayerMask(_MutateCall):
    """
    manages the functions for getting layer masks
    the __call__ method will be the function selected for the passed atlas

    these functions accept a layer name and return a mask from the atlas
    layer names are provided in their uppercase string forms
    """

    def __init__(self, atlas):
        self._atlas = atlas
        if atlas.load_region_map().find('@^L1$|.*;L1$', 'acronym')\
           or atlas.load_region_map().find("@^SP$|.*;SP$", 'acronym'):
            self._method = self.full_layer
        elif atlas.load_region_map().find("@.*;1$", 'acronym'):
            self._method = self.column_semicolon_int
        else:
            self._method = self.ABI

    def column_semicolon_int(self, layer):
        """layer acronyms are <column>;<layer_number. e.g. mc2;2"""
        return self._atlas.get_region_mask(
            "@;{}$".format(layer[1]), attr="acronym").raw

    def full_layer(self, layer):
        """layer acronyms contain the full layer string, e.g L2 or mc2;L2"""
        return self._atlas.get_region_mask(
            "@{}$".format(layer), attr="acronym").raw

    def ABI(self, layer):
        """
        layer acronyms according to the BlueBrainAtlas
        for cortex this is the layer number at the end of the region name
        for hippocampus it is the lowercase layer name
        at the end of the region name
        """
        if layer.startswith('L') and layer[1] in '123456':
            # cortex
            return self._atlas.get_region_mask("@.*{}$".format(layer[1:])).raw
        else:
            # hippocampus
            return self._atlas.get_region_mask(
                "@.*{}$".format(layer.lower())).raw


class _RegionMask(_MutateCall):
    """
    manages _region_mask function varieties

    sets its __call__ method

    these functions accept a region acronym provided by a query and
    return a mask from the atlas (if relevant)
    acronym provided will be based on ABI/BBA naming conventions
    """

    def __init__(self, atlas):
        self._atlas = atlas
        if is_O1_atlas(atlas):
            self._method = self.O1_no_region_mask
        elif is_paxinos_watson(atlas):
            self._method = self.Paxinos_regions
        else:
            self._method = self.BBA_ABI_verbatim

    def O1_no_region_mask(self, region):
        """O1 circuits don't have 'region'
        in the same sense as whole brain atlas"""
        warn(Warning("{} ignores 'region' as it is not relevant to O1 atlas"
                     .format(self)))
        return self._atlas.load_data("brain_regions").raw != 0

    def BBA_ABI_verbatim(self, region):
        """simply request the region from the atlas if it conforms to
        the BBA naming conventions"""
        return self._atlas.get_region_mask(region).raw

    def Paxinos_regions(self, ABI_region):
        pax_region = ABI_region.replace("SSp", "S1").replace("-bfd", "BF")\
                     .replace("-ul", "FL").replace("-ll", "HL")\
                     .replace("-m", "J").replace("-tr", "Tr")\
                     .replace("-dz", "DZ").replace("-dzo", "DZO")\
                     .replace("-sh", "Sh").replace("-ulp", "ULp")\
                     .replace("SS", "SSCtx").replace("SSs", "S2")
        return self._atlas.get_region_mask(pax_region).raw


class _ColumnMask(_MutateCall):
    """
    container for _column_mask function varieties

    these functions accept a column in the form mc<column_number>
    and return a corresponding mask from the atlas, if relevant
    """

    def __init__(self, atlas):
        self._atlas = atlas
        if is_O1_atlas(atlas):
            self._method = self.O1_column
        else:
            self._method = self.no_columns

    def O1_column(self, column):
        """O1 circuits have columns in their regions"""
        return self._atlas.get_region_mask(column + "_Column").raw

    def no_columns(self, column):
        """columns are not defined for this atlas"""
        warn(Warning("column is not defined for {}, ignoring".format(self)))
        return self._atlas.load_data("brain_regions").raw != 0


class _CellDensityGenerator(_MutateCall):
    """
    just a container for cell_density function varieties

    the cell_density function accepts a query containing data on where to
    get density (layer, region, column ... ) and what kind (sclass, mtype...)
    and returns a value for each voxel in the target area
    """

    # TODO: maybe method/object names should be plural, as they return lists
    def __init__(self, atlas):
        self._atlas = atlas
        if has_cell_density(atlas):
            self._method = self.has_density
            self._total_density = _TotalDensity(atlas, self)
            self._mtype_filename = _MtypeFilename(atlas)
            self._sclass_filename = _SclassFilename(atlas)
        else:
            self._method = self.no_cell_density

    def no_cell_density(self, query):
        """no density data in this atlas"""
        warn(Warning("{} atlas has no cell density, returning NaN"
                     .format(self)))
        return np.nan

    def has_density(self, query):
        """get density data from the atlas"""
        if 'mtype' in query:
            density_types = [name
                             for mtype in _list_if_not_list(query['mtype'])
                             for name in
                             _list_if_not_list(self._mtype_filename(mtype))]
            if 'sclass' in query:
                warn(Warning(
                    'mtype keyword overrides sclass in cell_density'
                    .format(self)))

        elif 'sclass' in query:
            density_types = [scname
                             for sclass in _list_if_not_list(query['sclass'])
                             for scname in self._sclass_filename(sclass)]
        else:
            density_types = self._total_density()

        densities = [
            self._atlas.load_data(density_type).raw
            for density_type in density_types]
        if len(densities) == 0:
            return np.nan
        print(density_types)
        return np.nansum(densities, axis=0)


class _TotalDensity(_MutateCall):
    """
    just a container for the _total_density function varieties

    these functions accept no arguments and simply return the list of
    density filenames that add up to form total density
    """

    # TODO: think about how organise this object.
    #       How should it interface with _sclass_filename and _mtype_filename
    def __init__(self, atlas, _cell_density):
        self._parent_cd_object = _cell_density
        self._atlas = atlas
        if has_sclass_densities(atlas):
            self._method = self.exc_and_inh
        else:
            self._method = self.all_mtypes

    def exc_and_inh(self):
        """
        total density is the sum of excitatory and inhibitory density
        """
        return [scname
                for sclass in ('EXC', 'INH')
                for scname in self._parent_cd_object._sclass_filename(sclass)]

    def all_mtypes(self):
        """
        total density is the sum of all mtype densities
        """
        import glob
        from os.path import basename, join
        allnrrdnames = [basename(nrrd).split(".")[0] for nrrd in
                        glob.glob(join(self._atlas.dirpath, "*.nrrd"))]

        mtype_names = [fname for mtype in BIG_LIST_OF_KNOWN_MTYPES
                       for fname in _list_if_not_list(
                               self._parent_cd_object._mtype_filename(mtype))]
        all_mtypes = {
            fname for fname in allnrrdnames if fname in mtype_names}

        return list(all_mtypes)


class _SclassFilename(_MutateCall):
    """
    just a container for _sclass_filename function varieties

    these functions accept the name of the density type
    (e.g. the sclass or mtype name) and return a list of filenames that
    add up to the density for that type.
    """

    def __init__(self, atlas):
        self._atlas = atlas
        # TODO: disentangle presence of sclass from prefix
        if has_sclass_densities(atlas):
            self._method = self.bracketed_prefix
        else:
            self._method = self.has_no_sclass

    # TODO: split BIG_LIST by sclass, so that sclass density can be
    #       obtained from mtype densities?
    def has_no_sclass(self, density_type):
        """the circuit has no information about sclass density"""
        warn(Warning("{} has no sclass densities".format(self)))
        return []

    def bracketed_prefix(self, density_type):
        """
        the sclass density is contained in files named
        [cell_density]<sclass>.nrrd
        """

        # for now assume no UN
        if density_type in ("EXC", "INH"):
            return ['[cell_density]' + density_type]
        else:
            return []


class _MtypeFilename(_MutateCall):
    """just a container for _mtype_filename function varieties"""

    def __init__(self, atlas):
        self._atlas = atlas
        if has_layer_prefixed_mtypes(atlas):
            self._method = self.layer_prefix
        else:
            self._method = self.no_prefix

    def layer_prefix(self, mtype):
        """mtype densities are stored with a prefix"""
        from glob import glob
        from os.path import join, basename
        allnames = glob(
            join(self._atlas.dirpath, "*_" + mtype + ".nrrd"))
        basenames = [basename(name).split(".")[0]
                     for name in allnames]
        return basenames

    def no_prefix(self, mtype):
        """mtype densities are stored with a direct name"""
        return mtype
