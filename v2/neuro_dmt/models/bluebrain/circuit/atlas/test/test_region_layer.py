"""
Test `class RegionLayer` and it's associated code.
"""
from voxcell.nexus.voxelbrain import Atlas
from ..region_layer import *
from . import *

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
    assert FullLayerRepresentation(atlas)._use_paxinos_regions

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
    representation = RegionLayerRepresentation.for_atlas(atlas)
    assert not BlueBrainAtlasRepresentation(atlas)._use_paxinos_regions

    expect_equal(
        representation.get_region_acronym("SSp"),
        "SSp",
        "atlas: {}".format(atlas_name))
    expect_equal(
        representation.get_layer_region_regex("L2"),
        "@.*2$",
        "atlas: {}".format(atlas_name))


