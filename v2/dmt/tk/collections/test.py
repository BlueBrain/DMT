"""
Test develop collections.
"""
from . import  get_list

def test_get_list():
    """
    Get list should return list from singletons, as well as list-like...
    """
    a_list = get_list("a")
    assert len(a_list) == 1
    assert a_list[0] == "a"

    ab = ['a', 'b']
    ab_list = get_list(*ab)

    assert len(ab_list) == len(ab)
    assert ab_list[0] == ab[0]
    assert ab_list[1] == ab[1]
