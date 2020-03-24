"""
Test develop `Phenomenon`.
"""

from .import Phenomenon

phenomenon = Phenomenon(
    name="Cell Density",
    description="""Cell density is the number of cells in a unit volume in the
    circuit. Preferable units to represent cell density are count per unit
    milli-meter cube.""")

def test_phenomenon_label():
    """
    Test `Phenomenon` label.
    """
    assert phenomenon.label == "cell_density",\
        "Phenomenon label {}".format(phenomenon.label)

def test_phenomenon_group():
    """
    If not specified, a `Phenomenon`'s group must be the same as it's label.
    """
    assert phenomenon.group == phenomenon.label

def test_eq():
    """
    Two `Phenomenon`s differing only by typos in their descriptions, should be
    considered as equal.
    """
    phenomenon_typoed = Phenomenon(
        name="Cell    Density",
        description="""Cell density  is the number of cells in a unit volume in 
        the circuit. Preferable units to represent cell density are count per 
        unit milli-meter cube.     """)
