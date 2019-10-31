"""
Test nesting, unnesting
"""

from ..import index_tree

def test_unnesting():
    """
    `index_tree.as_unnested_tree` should be able to flatten the keys
    of a nested dict.
    """
    nested_dict = dict(
        x0=dict(
            y0=dict(z0=0, z1=1),
            y1=dict(z0=2, z1=3)),
        x1=dict(
            y0=dict(z0=4, z1=5),
            y1=dict(z0=6, z1=7)))
    unnested_dict = index_tree.as_unnested_dict(nested_dict)
    assert ("x0", "y0", "z0") in unnested_dict
    assert unnested_dict[("x0", "y0", "z0")] == 0
    assert ("x0", "y0", "z1") in unnested_dict
    assert unnested_dict[("x0", "y0", "z1")] == 1
    assert ("x0", "y1", "z0") in unnested_dict
    assert unnested_dict[("x0", "y1", "z0")] == 2
    assert ("x0", "y1", "z1") in unnested_dict
    assert unnested_dict[("x0", "y1", "z1")] == 3
    assert ("x1", "y0", "z0") in unnested_dict
    assert unnested_dict[("x1", "y0", "z0")] == 4
    assert ("x1", "y0", "z1") in unnested_dict
    assert unnested_dict[("x1", "y0", "z1")] == 5
    assert ("x1", "y1", "z0") in unnested_dict
    assert unnested_dict[("x1", "y1", "z0")] == 6
    assert ("x1", "y1", "z1") in unnested_dict
    assert unnested_dict[("x1", "y1", "z1")] == 7

