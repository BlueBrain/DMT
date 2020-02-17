"""
classes and methods for adapting atlases
"""
import os
from os.path import basename, join
import numpy as np
import glob
from warnings import warn
from voxcell.nexus.voxelbrain import Atlas
from voxcell import VoxcellError
from dmt.tk import terminology
from neuro_dmt import terminology
from neuro_dmt.terminology.atlas import translate
# TODO: what if components were made into MethodTypes - __call__
#       calling their own methods based on atlas properties
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
# TODO: atlasSpec
# TODO: move each component to its own file, write component-level tests
BIG_LIST_OF_KNOWN_MTYPES = [
    "RC", "IN", "TC", "BPC", "BP", "BTC", "CHC", "DAC", "DBC", "HAC", "HPC",
    "IPC", "LAC", "LBC", "MC", "NBC", "NGC-DA", "NGC-SA", "NGC", "SAC", "SBC",
    "SSC", "TPC:A", "TPC:B", "TPC:C", "TPC", "UPC"]


def _list_if_not_list(item):
    """make something a list if it isn't an iterable"""
    if isinstance(item, str):
        return [item]
    try:
        len(item)
        return item
    except TypeError:
        return [item]


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


def has_PHy(atlas):
    return os.path.exists(os.path.join(atlas.dirpath, "[PH]y.nrrd"))


class _LayerMask:
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
            self.get = self.full_layer
        elif atlas.load_region_map().find("@.*;1$", 'acronym'):
            self.get = self.column_semicolon_int
        else:
            self.get = self.ABI

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
            # TODO: I somehow missed L6 in my test cases!!??
            return self._atlas.get_region_mask("@.*{}[ab]?$".format(layer[1:])).raw
        else:
            # hippocampus
            return self._atlas.get_region_mask(
                "@.*{}$".format(layer.lower())).raw


class _RegionMask():
    """
    manages _region_mask function varieties

    sets its __call__ method

    these functions accept a region acronym provided by a parameters and
    return a mask from the atlas (if relevant)
    acronym provided will be based on ABI/BBA naming conventions
    """

    def __init__(self, atlas):
        self._atlas = atlas
        if is_O1_atlas(atlas):
            self.get = self.O1_no_region_mask
        elif is_paxinos_watson(atlas):
            self.get = self.Paxinos_regions
        else:
            self.get = self.BBA_ABI_verbatim

    def O1_no_region_mask(self, region):
        """O1 circuits may not have terminology.circuit.region
        in the same sense as whole brain atlas"""
        warn(Warning(
            "{} ignores terminology.circuit.region as it is not relevant to O1 atlas"
            .format(self)))
        return self._atlas.load_data("brain_regions").raw != 0

    def BBA_ABI_verbatim(self, region):
        """simply request the region from the atlas if it conforms to
        the BBA naming conventions"""
        return self._atlas.get_region_mask(region).raw

    def Paxinos_regions(self, ABI_region):
        pax_region = translate.ABI_to_Paxinos(ABI_region)
        return self._atlas.get_region_mask(pax_region).raw


class _ColumnMask:
    """
    manages the functions for getting column masks

    these functions accept a column in the form mc<column_number>
    and return a corresponding mask from the atlas, if relevant
    """

    def __init__(self, atlas):
        self._atlas = atlas
        if is_O1_atlas(atlas):
            self.get = self.O1_column
        else:
            self.get = self.no_columns

    def O1_column(self, column):
        """O1 circuits have columns in their regions"""
        return self._atlas.get_region_mask(column + "_Column").raw

    def no_columns(self, column):
        """columns are not defined for this atlas"""
        warn(Warning("column is not defined for {}, ignoring".format(self)))
        return self._atlas.load_data("brain_regions").raw != 0


def _get_PHy_depth(atlas):
    try:
        phy = atlas.load_data("[PH]y").raw
        top = atlas.load_data("[PH]1").raw[..., 1]
    except VoxcellError:
        raise NotImplementedError("No depth data available for this atlas {}"
                                  .format(atlas.dirpath))
    return top - phy


def _get_PHy_height(atlas):
    try:
        phy = atlas.load_data("[PH]y").raw
        bot = atlas.load_data("[PH]6").raw[..., 0]
        return phy - bot
    except VoxcellError:
        return atlas.load_data("distance").raw


class _PrincipalAxisPositionMask:

    def __init__(self, atlas):
        self._atlas = atlas

    def get_depth(self):
        return _get_PHy_depth(self._atlas)

    def get_height(self):
        return _get_PHy_height(self._atlas)

    def get(self, absolute_depth=None, absolute_height=None):
        if absolute_depth is not None and absolute_height is not None:
            raise RuntimeError("cannot provide both depth and height")
        elif absolute_depth is not None:
            vol = self.get_depth()
            value = absolute_depth
        elif absolute_height is not None:
            vol = self.get_height()
            value = absolute_height
        else:
            raise RuntimeError("asked for mask with no parameters")
        return (np.logical_and(vol >= value[0], vol < value[1])
                if isinstance(value, tuple) else vol == value)


# TODO: separate principal axes from the rest
class _AtlasMasks:
    """helper class for CircuitAtlas,
    handles getting the mask for a parameters"""

    _LayerMask = _LayerMask
    _RegionMask = _RegionMask
    _ColumnMask = _ColumnMask
    _PrincipalAxisPositionMask = _PrincipalAxisPositionMask

    def __init__(self, atlas, represented_region=None):
        self._atlas = atlas
        self._layer_mask = self._LayerMask(atlas)
        self._region_mask = self._RegionMask(atlas)
        self._column_mask = self._ColumnMask(atlas)
        self._pa_position_mask = self._PrincipalAxisPositionMask(atlas)
        self.represented_region = represented_region

    def get(self, parameters):
        """get the mask for parameters"""
        masks = [self._atlas.load_data("brain_regions").raw > 0]

        if terminology.circuit.region in parameters:
            region_mask = np.any(
                [self._region_mask.get(region)
                 for region in _list_if_not_list(
                         parameters[terminology.circuit.region])],
                axis=0)
            masks.append(region_mask)

        if terminology.circuit.layer in parameters:
            layer_mask = np.any(
                [self._layer_mask.get(layer)
                 for layer in _list_if_not_list(
                         parameters[terminology.circuit.layer])],
                axis=0)
            masks.append(layer_mask)

        if terminology.circuit.mesocolumn in parameters:
            column_mask = np.any(
                [self._column_mask.get(column)
                 for column in _list_if_not_list(
                         parameters[terminology.circuit.mesocolumn])], axis=0)
            masks.append(column_mask)

        def list_if_1depth_tup(tup):
            try:
                len(tup[0])
                return tup
            except TypeError:
                return [tup]

        if terminology.circuit.depth in parameters:
            depth_mask = np.any(
                [self._pa_position_mask.get(
                    absolute_depth=absd)
                 for absd in list_if_1depth_tup(
                         parameters[terminology.circuit.depth])],
                axis=0)
            masks.append(depth_mask)

        if terminology.circuit.height in parameters:
            height_mask = np.any(
                [self._pa_position_mask.get(
                    absolute_height=absd)
                 for absd in list_if_1depth_tup(
                         parameters[terminology.circuit.height])],
                axis=0)
            masks.append(height_mask)

        if self.represented_region is not None:
            masks.append(self.represented_region)
        return np.all(masks, axis=0)

    # TODO: depths stuff is not really a subset of Masks
    #       but masks does not (should not?) have access to CircuitAtlas
    #       instance, so we can't leave it there
    def get_depth_volume(self):
        return self._pa_position_mask.get_depth()


class _TotalDensity:
    """
    container for _total_density function varieties

    these functions return a list of filenames of nrrds
    that sum to total density
    """

    # TODO: think about how organise this object.
    #       How should it interface with _sclass_filename and _mtype_filename
    def __init__(self, atlas, _cell_density):
        self._parent_cd_object = _cell_density
        self._atlas = atlas
        if has_sclass_densities(atlas):
            self.get = self.exc_and_inh
        else:
            self.get = self.all_mtypes

    def exc_and_inh(self):
        """
        total density is the sum of excitatory and inhibitory density
        """
        return [scname
                for sclass in ('EXC', 'INH')
                for scname in
                self._parent_cd_object._sclass_filename.get(sclass)]

    def all_mtypes(self):
        """
        total density is the sum of all mtype densities
        """
        allnrrdnames = [basename(nrrd).split(".")[0] for nrrd in
                        glob.glob(join(self._atlas.dirpath, "*.nrrd"))]

        mtype_names = [fname for mtype in BIG_LIST_OF_KNOWN_MTYPES
                       for fname in _list_if_not_list(
                            self._parent_cd_object._msc_filename.get(mtype))]
        all_mtypes = {
            fname for fname in allnrrdnames if fname in mtype_names}

        return list(all_mtypes)


class _SclassFilename:
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
            self.get = self.bracketed_prefix
        else:
            self.get = self.has_no_sclass

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


class _MtypeFilename:

    def __init__(self, atlas):
        self._atlas = atlas
        if has_layer_prefixed_mtypes(atlas):
            self.get = self.with_prefix
        else:
            self.get = self.plain_msubclass
        return

    def with_prefix(self, mtype):
        """stored including layer prefix and potential other prefix"""
        return [basename(fn).split(".")[0] for fn in
                glob.glob(join(self._atlas.dirpath, "*" + mtype + "*"))]

    def plain_msubclass(self, mtype_name):
        """stored as morphology_subclass"""
        # TODO: have to restrict this to layer
        return [mtype_name.split("_")[0]]


class _MSClassFilename:
    """methods for getting densities of morphology_subclass"""

    def __init__(self, atlas):
        self._atlas = atlas
        if has_layer_prefixed_mtypes(atlas):
            self.get = self.layer_prefix
        else:
            self.get = self.no_prefix

    def layer_prefix(self, msubclass):
        """msubclass densities are stored with a prefix"""
        allnames = glob.glob(
            join(self._atlas.dirpath, "*_" + msubclass + ".nrrd"))
        basenames = [basename(name).split(".")[0]
                     for name in allnames]
        return basenames

    def no_prefix(self, msubclass):
        """msubclass densities are stored with a direct name"""
        return msubclass


class _CellDensity:
    """
    manages varieties of functions for getting cell density

    the cell_density function accepts a parameters containing data on where to
    get density (layer, region, column ... ) and what kind (sclass, mtype...)
    and returns a value for each voxel in the target area
    """

    # TODO: maybe method/object names should be plural, as they return lists
    def __init__(self, atlas):
        self._atlas = atlas
        if has_cell_density(atlas):
            self.get = self.has_density
            self._total_density = _TotalDensity(atlas, self)
            self._msc_filename = _MSClassFilename(atlas)
            self._mtype_filename = _MtypeFilename(atlas)
            self._sclass_filename = _SclassFilename(atlas)
        else:
            self.get = self.no_cell_density

    def no_cell_density(self, parameters):
        """no density data in this atlas"""
        warn(Warning("{} atlas has no cell density, returning NaN"
                     .format(self._atlas)))
        return np.nan

    def has_density(self, parameters):
        """get density data from the atlas"""
        if terminology.circuit.mtype in parameters:
            density_types = [dens
                             for mtype in
                             _list_if_not_list(parameters[terminology.circuit.mtype])
                             for dens in self._mtype_filename.get(mtype)]
        elif terminology.cell.morphology_subclass in parameters:
            density_types = [name
                             for msc in _list_if_not_list(
                                     parameters[terminology.cell.morphology_subclass])
                             for name in _list_if_not_list(
                                     self._msc_filename.get(msc))]
            if terminology.cell.synapse_class in parameters:
                warn(Warning(
                    'mtype keyword overrides sclass in {}.cell_density'
                    .format(self)))

        elif terminology.cell.synapse_class in parameters:
            density_types = [scname
                             for sclass in _list_if_not_list(
                                     parameters[terminology.cell.synapse_class])
                             for scname in self._sclass_filename.get(sclass)]
        else:
            density_types = self._total_density.get()

        if len(density_types) == 0:
            return np.nan

        densities = self._atlas.load_data(density_types[0]).raw
        for density_type in density_types[1:]:
            densities = np.nansum(
                [densities, self._atlas.load_data(density_type).raw], axis=0)
        return densities


_SPATIAL = (
    terminology.circuit.layer,
    terminology.circuit.region,
    terminology.circuit.mesocolumn,
    terminology.circuit.height,
    terminology.circuit.depth)


# TODO: construct with automatic mixins rather than aggregation
#       (is that really better?)
class CircuitAtlas:
    """adapter for a wide set of atlases"""

    def __init__(self, path, represented_region=None):
        """initialize the adapter for the atlas"""
        self._atlas = Atlas.open(path)
        self._masks = _AtlasMasks(self._atlas,
                                  represented_region=represented_region)
        self._cell_density = _CellDensity(self._atlas)
        self.voxel_volume =\
            self._atlas.load_data("brain_regions").voxel_volume

    def voxeldata(self, array):
        """convert an array to voxeldata with this atlas' metatdata"""
        return self._atlas.load_data("brain_regions").with_data(array)

    @terminology.use(*_SPATIAL)
    def get_mask(self, **parameters):
        """get a mask corresponding to parameters"""
        # delegate
        return self._masks.get(parameters)

    @terminology.use(*_SPATIAL,
                     terminology.cell.morphology_subclass,
                     terminology.cell.synapse_class,
                     terminology.cell.mtype)
    def cell_density(self, **parameters):
        """get atlas cell density"""
        density_volume = self._cell_density.get(parameters)
        if np.all(np.isnan(density_volume)):
            return np.nan
        spatial_params = {param: value
                          for param, value in parameters.items()
                          if param in _SPATIAL}
        return np.mean(density_volume[self.get_mask(**spatial_params)])

    # TODO: methods like these might like some parameters too
    @terminology.use(*_SPATIAL)
    def depths(self, **parameters):
        if parameters is None:
            parameters = {}
        depth = _get_PHy_depth(self._atlas)[
            self.get_mask(**parameters)]
        return np.unique(depth[np.isfinite(depth)])

    @terminology.use(*_SPATIAL)
    def heights(self, **parameters):
        if parameters is None:
            parameters = {}
        height = _get_PHy_height(self._atlas)[
            self.get_mask(**parameters)]
        return np.unique(height[np.isfinite(height)])