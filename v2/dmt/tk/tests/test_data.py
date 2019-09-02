import pandas as pd
from pandas import testing as pdt
from dmt.tk.data import parameters_to_df


def test_plain_dict():
    testdict = {'a': [1, 2, 3, 4], 'b': 0}
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, parameters_to_df(testdict))


def test_list_of_dict():
    testdict = [{'a': 1, 'b': 0}, {'a': 2, 'b': 0}, {'a': 3}]
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, parameters_to_df(testdict))


def test_list_entries():
    testdict = {'c': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, parameters_to_df(testdict))


def test_list_dicts():
    testdict = [{'c': a} for a in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, parameters_to_df(testdict))


def test_one_list():
    testdict = {'c': [[1, 2, 3], 5, [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 5, 7], ('c', 1): [2, None, 8],
                          ('c', 2): [3, None, 9]})
    print(expdf, parameters_to_df(testdict))
    pdt.assert_frame_equal(expdf, parameters_to_df(testdict))
