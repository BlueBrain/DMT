"""Test develop Condition"""

from dmt.vtk.measurement.condition\
    import Condition

def test_condition_hash():
    """We implement a __hash__ method for class Condition"""
    def get_condition(layer, mtype):
        return Condition([
            ("layer", layer),
            ("region", "SSp-ll"),
            ("mtype", mtype)])
    c1 = get_condition(1, "L1_TPC:A")
    c2 = get_condition(2, "L2_TPC:B")
    c3 = get_condition(2, "L2_TPC:B")
    d = {c1.hash_id: 1000,
         c2.hash_id: 2000}
    d[c3.hash_id] = 3000

    return d

