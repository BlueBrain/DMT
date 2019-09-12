"""
Test develop the behavior of CircuitAtlas
"""

import os
import numpy as np
import numpy.testing as npt
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.field import WithFields, Field, lazyfield
from . import CircuitAtlas
from .region_layer import *

def project(number):
    return "/gpfs/bbp.cscs.ch/project/proj{}".format(number)

path_atlas = {
    "O1MouseSSCx": os.path.join(
        project(66),
        "entities/dev/atlas/O1-152"),
    "O1RatSSCxDiss": os.path.join(
        project(64),
        "dissemination/data/atlas/O1/MEAN/mean"),
    "S1RatSSCx": os.path.join(
        project(64),
        "entities/dev/atlas/",
        "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"),
    "O1MouseHip": os.path.join(
        project(42),
        "entities/dev/atlas/",
        "20190625-CA3-O1-atlas/"),
    "S1MouseNeoCx": os.path.join(
        project(68),
        "entities/",
        "dev/atlas/ccf_2017-50um/20181114"),
    "S1RatSSCxDiss": os.path.join(
        project(64),
        "dissemination",
        "data/atlas/S1/MEAN/juvenile_L23_MC_BTC_shifted_down",
        "Bio_M")}


def test_atlas_paths():
    """
    Paths in `path_atlas` must exist.
    """
    for name_atlas, path in path_atlas.items():
        assert Atlas.open(path),\
            "Could not open atlas {} at {}.".format(name_atlas, path)


def _expect_equal(x, y):
    assert x == y, "{} != {}".format(x, y)

def test_representation_applicability():
    """
    One of the `RegionLayerRepresentation`s should apply.
    """
    path = path_atlas["S1RatSSCxDiss"]
    atlas = Atlas.open(path)
    assert FullLayerRepresentation.is_applicable(atlas)
    assert not SemicolonIntRepresentation.is_applicable(atlas)
    assert not BlueBrainAtlasRepresentation.is_applicable(atlas)
    representation = RegionLayerRepresentation.for_atlas(atlas)
    assert FullLayerRepresentation(atlas)._use_paxinos_regions

    _expect_equal(
        representation.get_region_acronym("SSp"),
        "S1")
    _expect_equal(
        representation.get_layer_region_regex("L1"),
        "@L1$")

class CircuitAtlasTest(WithFields):
    """
    Test `CircuitAtlas`.
    """
    path_atlas = Field(
        """
        Path to the atlas to be tested.
        """)

    region_acronyms = Field(
        """
        A list of acronyms to test with.
        """)

    @lazyfield
    def circuit_atlas(self):
        """
        `CircuitAtlas` instance to be tested.
        """
        return CircuitAtlas(path=self.path_atlas)

    @lazyfield
    def atlas(self):
        """
        `Atlas` instance to test against.
        """
        return Atlas.open(self.path_atlas)

    def region_mask(self):
        for region in self.region_acronyms:
            atlas_region = self\
                .circuit_atlas\
                .region_layer_representation\
                .get_region_acronym("SSp")
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(region=region),
                self.atlas.get_region_mask(atlas_region).raw)


def test_S1RatSSCxDiss():
    """
    Test Rat SSCx Dissemination atlas.
    """
    name_atlas = "S1RatSSCxDiss"
    circuit_atlas_test =\
        CircuitAtlasTest(
            path_atlas=path_atlas[name_atlas],
            region_acronyms=["SSp"])
    circuit_atlas = circuit_atlas_test.circuit_atlas
    atlas = circuit_atlas_test.atlas

    circuit_atlas_test.region_mask()
