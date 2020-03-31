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
Test `class RegionLayer` and it's associated code.
"""
from voxcell.nexus.voxelbrain import Atlas
from ..region_layer import *
from . import *

def test_acronym_generator():
    """
    `RegionAcronymGenerator` should provide good region acronyms.
    """
    name_atlas =\
        "O1MouseSSCx"
    region_acronym =\
        RegionAcronymGenerator.for_atlas(
            Atlas.open(path_atlas[name_atlas]))
    expect_equal(
        region_acronym.get("mc0"),
        "mc0_Column",
        "atlas: {}".format(name_atlas))
    expect_equal(
        region_acronym.get("L1"),
        "L1",
        "atlas: {}".format(name_atlas))

    name_atlas =\
        "S1RatSSCxDiss"
    atlas =\
        Atlas.open(path_atlas[name_atlas])
    assert PaxinosBrainAtlasRegions.is_applicable(atlas),\
        "{} should be a Paxinos-Watson atlas".format(name_atlas)
    region_acronym =\
        RegionAcronymGenerator.for_atlas(atlas)
    expect_equal(
        region_acronym.get("SSp-ll"),
        "S1HL",
        "atlas: {}".format(name_atlas))

    expect_equal(
        region_acronym.get("SSp-ll;L1"),
        "S1HL;L1",
        "atlas: {}".format(name_atlas))

def test_representation_applicability():
    """
    One of the `RegionLayerRepresentation`s should apply.
    """
    atlas_name = "S1RatSSCxDiss"
    path = path_atlas[atlas_name]
    atlas = Atlas.open(path)
    assert FullLayerRepresentation.is_applicable(atlas)
    assert not SemicolonIntRepresentation.is_applicable(atlas)
    assert not BlueBrainAtlasRepresentation.is_applicable(atlas)
    representation = RegionLayerRepresentation.for_atlas(atlas)

    expect_equal(
        representation.get_region_acronym("SSp"),
        "S1",
        "atlas: ".format(atlas_name))
    expect_equal(
        representation.get_layer_region_regex("L1"),
        "@L1$",
        "atlas: {}".format(atlas_name))

    atlas_name = "S1MouseNeoCx"
    path = path_atlas[atlas_name]
    atlas = Atlas.open(path)
    assert not FullLayerRepresentation.is_applicable(atlas)
    assert not SemicolonIntRepresentation.is_applicable(atlas)
    assert BlueBrainAtlasRepresentation.is_applicable(atlas)

def test_layer_region_ids():
    """
    `RegionLayer` should be able to retrieve ids for layer regions.
    """
    name_atlas =\
        "O1MouseSSCx"
    atlas =\
        Atlas.open(path_atlas[name_atlas])
    region_layer =\
        RegionLayer(atlas=atlas)
    expect_equal(
        region_layer.get_ids(region="mc0", layer="L6"), {8})
    expect_equal(
        region_layer.get_ids(region="mc0", layer="L1"), {43})
    expect_equal(
        region_layer.get_ids(region="mc6", layer="L6"), {14})
    expect_equal(
        region_layer.get_ids(region="mc6", layer="L1"), {49})

    atlas_name =\
        "S1RatSSCxDiss"
    atlas =\
        Atlas.open(path_atlas[atlas_name])
    region_layer =\
        RegionLayer(atlas=atlas)

    expect_equal(
        region_layer.get_ids(region="SSp-ll", layer="L1"), {1125})
    expect_equal(
        region_layer.get_ids(region="SSp-ll", layer="L6"), {1130})

    atlas_name =\
        "S1MouseNeoCx"
    atlas =\
        Atlas.open(path_atlas[atlas_name])
    region_layer =\
        RegionLayer(atlas=atlas)

    expect_equal(
        region_layer.get_ids(region="SSp-ll", layer="L1"), {1030})
    expect_equal(
        region_layer.get_ids(region="SSp-ll", layer="L6"), {478, 510})
