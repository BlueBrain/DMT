# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
classes and methods for adapting atlases
"""
import os
from abc import ABC, abstractmethod
import numpy as np
import glob
from enum import Enum
from warnings import warn
from voxcell.nexus.voxelbrain import Atlas
from voxcell import VoxcellError
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.terminology.parameters import\
    MTYPE, SYN_CLASS, BRAIN_REGION,\
    COLUMN, LAYER,\
    DEPTH, HEIGHT
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
    """make something a list if it isn't"""
    if isinstance(item, list):
        return item
    return [item]


def is_O1_atlas(atlas):
    return len(atlas.load_region_map().find("O1 mosaic", "name")) > 0

def is_paxinos_watson(atlas):
    """
    Check if region acronyms corresponding to Paxiwos-Watson based
    Somatosensory atlas are present.
    """
    rmap = atlas.load_region_map()
    return rmap.find("SSCtx", "acronym") or rmap.find("S1HL", 'acronym')

def _nrrd(file_head, *file_tail):
    """
    Arguments
    file_head: Name of a file
    file_tail: A sequence of file names
    """
    if len(file_tail) == 0:
        return "{}.nrrd".format(file_head)
    return ["{}.nrrd".format(f) for f in (file_head,) + file_tail]

def has_sclass_densities(atlas):
    """
    Check that a directory has `.nrrd` files for synapse class densities.
    """
    nrrds_sclass = set(
        _nrrd("[cell_density]EXC", "[cell_density]INH", "EXC", "INH"))
    files_atlas = set(
        os.listdir(atlas.dirpath))
    return len(files_atlas.intersection(nrrds_sclass)) > 0

def has_layer_prefixed_mtypes(atlas):
    """
    Check whether mtype densities with
    layer prefixes are present in the atlas.
    """
    return any(
        glob.glob(os.path.join(atlas.dirpath, "*_{}.nrrd".format(mtype)))
        for mtype in BIG_LIST_OF_KNOWN_MTYPES)

def has_prefixless_mtypes(atlas):
    """
    Check that mtype densities without layer prefix
    are present in the atlas.
    """
    nrrds_mtype = set(
        _nrrd(BIG_LIST_OF_KNOWN_MTYPES))
    files_atlas = set(
        os.listdir(atlas.dirpath))
    return len(nrrds_mtype.intersection(files_atlas)) > 0

def has_cell_density(atlas):
    """
    checks for any cell density data
    """
    return has_sclass_densities(atlas)\
        or has_layer_prefixed_mtypes(atlas)\
        or has_prefixless_mtypes(atlas)

def has_PHy(atlas):
    """
    Check if `atlas` has principal axis position dataset.
    """
    return os.path.exists(os.path.join(atlas.dirpath, _nrrd("[PH]y")))


class RegionLayerRepersentationType(Enum):
    Unknown = 0
    BlueBrainAtlas = 1
    FullAtlas = 2
    SemicolonInt = 3


class AtlasType(Enum):
    Unknown = 0
    PaxinosWatson = 1
    BlueBrain = 2
    O1 = 3


class RegionLayerRepresentation(WithFields):
    """
    Expresses how an atlas represents a brain-region's layer.
    """
    def __init__(self, atlas):
        """
        Initialize for an atlas.
        """
        pattern_full_layer_cortical = "@^L1$|.*;L1$"
        pattern_full_layer_hippocampal = "@^SP$|.*;SP$"
        pattern_semicolon_int = "@.*;1$"
        region_map = atlas.load_region_map()

        if (region_map.find(pattern_full_layer_cortical, "acronym") or 
            region_map.find(pattern_full_layer_hippocampal, "acronym")):
            self.region_layer_type = RegionLayerRepersentationType.FullAtlas
        elif region_map.find(pattern_semicolon_int, "acronym"):
            self.region_layer_type = RegionLayerRepersentationType.SemicolonInt
        else:
            self.region_layer_type = RegionLayerRepersentationType.BlueBrainAtlas

        if (region_map.find("SSCtx", "acronym") or
            region_map.find("S1HL", "acronym")):
            self.atlas_type = AtlasType.PaxinosWatson
        elif region_map.find("O1 mosaic", "name"):
            self.atlas_type = AtlasType.O1
        else:
            self.atlas_type = AtlasType.BlueBrain


    @lazyfield
    def acronym_pattern(self):
        """
        Regex pattern for layer region.
        """
        return {
            RegionLayerRepersentationType.BlueBrainAtlas: "@.*{}$",
            RegionLayerRepersentationType.FullAtlas: "@{}$",
            RegionLayerRepersentationType.SemicolonInt: "@;{}$"
        }[self.region_layer_type]

    def query_layer(self, layer):
        """
        Convert argument 'layer' to a query that the atlas supports.
        """
        if self.region_layer_type == RegionLayerRepersentationType.BlueBrainAtlas:
            return\
                layer[1:] if layer.startswith('L') and layer[1] in "123456"\
                else layer.lower()),
        if self.region_layer_type == RegionLayerRepersentationType.FullAtlas:
            return layer
        if self.region_layer_type == RegionLayerRepersentationType.SemicolonInt:
            return layer[1]

        raise TypeError(
            "Unknown RegionLayerRepresentationType {}".format(
                self.region_layer_type))

    def query_region(self, region):
        """
        Convert argument 'region' to a query that the atlas supports.
        """
        if self.atlas_type == AtlasType.O1:
            return None
        if self.atlas_type == AtlasType.BlueBrain:
            return region
        if self.atlas_type == AtlasType.PaxinosWatson:
            return translate.ABI_to_paxinos(region)

        raise TypeError(
            "Unknown AtlasType {}".format(
                self.atlas_type))
        
    def acronym(self, layer):
        """
        Acronym for layer.
        """
        return self.acronym_pattern.format(self.query_layer(layer))


class BlueBrainAtlasRegionLayerRepresentation(
        RegionLayerRepresentation):
    """
    Establish how BlueBrainAtlas represents layers in its hierarchy.
    """
    regex_pattern = "@.*{}$"

    def query_layer(self, layer):
        """
        Convert argument `layer` to a query that the atlas supports.
        """
        if layer.startswith('L') and layer[1] in "123456":
            return layer[1:]
        return layer.lower()


class FullLayerRegionLayerRepresentation(
        RegionLayerRepresentation):
    """
    """
    regex_pattern = "@{}$"

    def query_layer(self, layer):
        """
        Convert argument `layer` to a query that the atlas supports.
        """
        return layer


class RegionSemicolonIntRegionLayerRepresentation(
        RegionLayerRepresentation):
    """
    """
    acronym_pattern = "@;{}$"

    def query_layer(self, layer):
        """
        Convert argument `layer` to a query that the atlas supports.
        """
        return layer[1]


class _LayerMask(WithFields):
    """
    manages the functions for getting layer masks

    these functions accept a layer name and return a mask from the atlas
    layer names are provided in their uppercase string forms
    """
    atlas = Field(
        """
        `Atlas` instance in which this `_LayerMask` will provide masks.
        """)

    @lazyfield
    def region_layer_representation(self):
        """
        `RegionLayerRepresentation` for the `Atlas` instance for which
        layer masks will be generated.
        """
        return RegionLayerRepresentation(self.atlas)

    def get(self, layer, raw=True):
        """
        Get a region mask.
        """
        voxel_data =\
            self.atlas.get_region_mask(
                self.region_layer_representation.acronym(layer),
                attr="acronym")
        return voxel_data.raw if raw else voxel_data

    # def __init__(self, atlas):
    #     self._atlas = atlas
    #     if atlas.load_region_map().find('@^L1$|.*;L1$', 'acronym')\
    #        or atlas.load_region_map().find("@^SP$|.*;SP$", 'acronym'):
    #         self.get = self.full_layer
    #     elif atlas.load_region_map().find("@.*;1$", 'acronym'):
    #         self.get = self.column_semicolon_int
    #     else:
    #         self.get = self.ABI

    # def column_semicolon_int(self, layer):
    #     """layer acronyms are <column>;<layer_number. e.g. mc2;2"""
    #     return self._atlas.get_region_mask(
    #         "@;{}$".format(layer[1]), attr="acronym").raw

    # def full_layer(self, layer):
    #     """layer acronyms contain the full layer string, e.g L2 or mc2;L2"""
    #     return self._atlas.get_region_mask(
    #         "@{}$".format(layer), attr="acronym").raw

    # def ABI(self, layer):
    #     """
    #     layer acronyms according to the BlueBrainAtlas
    #     for cortex this is the layer number at the end of the region name
    #     for hippocampus it is the lowercase layer name
    #     at the end of the region name
    #     """
    #     if layer.startswith('L') and layer[1] in '123456':
    #         # cortex
    #         return self._atlas.get_region_mask("@.*{}$".format(layer[1:])).raw
    #     else:
    #         # hippocampus
    #         return self._atlas.get_region_mask(
    #             "@.*{}$".format(layer.lower())).raw


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
        """O1 circuits don't have BRAIN_REGION
        in the same sense as whole brain atlas"""
        warn(Warning("{} ignores BRAIN_REGION as it is not relevant to O1 atlas"
                     .format(self)))
        return self._atlas.load_data("brain_regions").raw != 0

    def BBA_ABI_verbatim(self, region):
        """simply request the region from the atlas if it conforms to
        the BBA naming conventions"""
        return self._atlas.get_region_mask(region).raw

    def Paxinos_regions(self, ABI_region):
        pax_region = translate_ABI_to_Paxinos(ABI_region)
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


class _AtlasMasks:
    """helper class for CircuitAtlas,
    handles getting the mask for a parameters"""

    def __init__(self, atlas, represented_region=None):
        self._atlas = atlas
        self._layer_mask = _LayerMask(atlas=atlas)
        self._region_mask = _RegionMask(atlas=atlas)
        self._column_mask = _ColumnMask(atlas=atlas)
        self._pa_position_mask = _PrincipalAxisPositionMask(atlas=atlas)
        self.represented_region = represented_region

    def get(self, parameters):
        """get the mask for parameters"""
        masks = [self._atlas.load_data("brain_regions").raw > 0]

        if BRAIN_REGION in parameters:
            region_mask = np.any(
                [self._region_mask.get(region)
                 for region in _list_if_not_list(parameters[BRAIN_REGION])],
                axis=0)
            masks.append(region_mask)

        if LAYER in parameters:
            layer_mask = np.any(
                [self._layer_mask.get(layer)
                 for layer in _list_if_not_list(parameters[LAYER])], axis=0)
            masks.append(layer_mask)

        if COLUMN in parameters:
            column_mask = np.any(
                [self._column_mask.get(column)
                 for column in _list_if_not_list(parameters[COLUMN])], axis=0)
            masks.append(column_mask)

        if DEPTH in parameters:
            depth_mask = np.any(
                [self._pa_position_mask.get(
                    absolute_depth=absd)
                 for absd in _list_if_not_list(parameters[DEPTH])],
                axis=0)
            masks.append(depth_mask)

        if HEIGHT in parameters:
            height_mask = np.any(
                [self._pa_position_mask.get(
                    absolute_height=absd)
                 for absd in _list_if_not_list(parameters[HEIGHT])],
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
        import glob
        from os.path import basename, join
        allnrrdnames = [basename(nrrd).split(".")[0] for nrrd in
                        glob.glob(join(self._atlas.dirpath, "*.nrrd"))]

        mtype_names = [fname for mtype in BIG_LIST_OF_KNOWN_MTYPES
                       for fname in _list_if_not_list(
                            self._parent_cd_object._mtype_filename.get(mtype))]
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
    """just a container for _mtype_filename function varieties"""

    def __init__(self, atlas):
        self._atlas = atlas
        if has_layer_prefixed_mtypes(atlas):
            self.get = self.layer_prefix
        else:
            self.get = self.no_prefix

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
        if MTYPE in parameters:
            density_types = [name
                             for mtype in _list_if_not_list(parameters[MTYPE])
                             for name in
                             _list_if_not_list(self._mtype_filename.get(mtype))]
            if SYN_CLASS in parameters:
                warn(Warning(
                    'mtype keyword overrides sclass in {}.cell_density'
                    .format(self)))

        elif SYN_CLASS in parameters:
            density_types = [scname
                             for sclass in _list_if_not_list(parameters[SYN_CLASS])
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


# TODO: perhaps adapter configuration should be something you can
#       pass to the adapter, to bypass automatic configuration?
#       this lets you manually specify traits when inference doesn't work
#       OPTION: abstract property inference to an AtlasSpec
class CircuitAtlas():
    """adapter for a wide set of atlases"""

    def __init__(self, atlas, represented_region=None):
        """initialize the adapter for the atlas"""
        if isinstance(atlas, Atlas):
            self._atlas = atlas
        else:
            self._atlas = Atlas.open(atlas)
        self._masks = _AtlasMasks(self._atlas,
                                  represented_region=represented_region)
        self._cell_density = _CellDensity(self._atlas)
        self.volume_voxel =\
            self._atlas.load_data("brain_regions").voxel_volume
        self.voxel_volume =\
            self._atlas.load_data("brain_regions").voxel_volume

    def mask_for_parameters(self, parameters):
        """get a mask corresponding to parameters"""
        # delegate
        return self._masks.get(parameters)

    def cell_density(self, parameters):
        """get atlas cell density"""
        density_volume = self._cell_density.get(parameters)
        if np.all(np.isnan(density_volume)):
            return np.nan
        return density_volume[self.mask_for_parameters(parameters)]

    # TODO: methods like these might like some parameters too
    def depths(self, parameters=None):
        if parameters is None:
            parameters = {}
        depth = _get_PHy_depth(self._atlas)[
            self.mask_for_parameters(parameters)]
        return np.unique(depth[np.isfinite(depth)])

    def heights(self, parameters=None):
        if parameters is None:
            parameters = {}
        height = _get_PHy_height(self._atlas)[
            self.mask_for_parameters(parameters)]
        return np.unique(height[np.isfinite(height)])
