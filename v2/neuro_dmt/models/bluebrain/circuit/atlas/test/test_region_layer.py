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
    representation = RegionLayerRepresentation.for_atlas(atlas)

    expect_equal(
        representation.get_region_acronym("SSp"),
        "SSp",
        "atlas: {}".format(atlas_name))
    expect_equal(
        representation.get_layer_region_regex("L2"),
        "@.*2$",
        "atlas: {}".format(atlas_name))


