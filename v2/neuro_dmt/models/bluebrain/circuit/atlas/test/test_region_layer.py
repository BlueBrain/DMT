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

    assert region_layer.get_ids(region="mc0") == {1}
    assert region_layer.get_ids(region=["mc0", "mc1"]) == {1,2}

    expect_equal(
        region_layer.get_ids(layer="L1"),
        {43, 44, 45, 46, 47, 48, 49})
    observed = region_layer.get_ids(region="mc0", layer="L6")
    assert 8 in observed, "8 not in {}" .format(observed)

    layers = ["L{}".format(l) for l in range(1, 7)]
    expected = {8, 15, 22, 29, 36, 43}
    observed = region_layer.get_ids(region="mc0", layer=layers)
    assert all(_id in observed for _id in expected)
    assert all(_id in expected for _id in observed)
