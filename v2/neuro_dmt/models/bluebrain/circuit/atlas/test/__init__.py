"""
Tests for `CircuitAtlas` and it's associated classes and code.
"""
import os
import numpy.testing as npt

def project(number):
    """
    Get path to the project, given its number.
    """
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

def expect_equal(x, y, message=""):
    try:
        message += " {} != {}".format(x, y)
        assert x == y, message
        return True
    except ValueError:
        if not message:
            message = """
            Array Left with sum {}
            != Array Right with sum {}
            """.format(
                np.nansum(x),
                np.nansum(y))
        npt.assert_array_equal(x, y, message)
        return True

    assert False, "Code execution should not reach here."



