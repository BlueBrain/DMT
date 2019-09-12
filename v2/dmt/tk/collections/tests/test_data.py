import pytest as pyt
import pandas as pd
from pandas import testing as pdt
from collections import OrderedDict
from dmt.tk.collections.data import multilevel_dataframe


def test_plain_dict():
    testdict = {'a': [1, 2, 3, 4], 'b': 0}
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_of_dict():
    testdict = [{'a': 1, 'b': 0}, {'a': 2, 'b': 0}, {'a': 3}]
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_entries():
    testdict = {'c': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_dicts_list():
    testdict = [{'c': a} for a in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_one_list():
    testdict = {'c': [[1, 2, 3], 5, [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 5, 7], ('c', 1): [2, None, 8],
                          ('c', 2): [3, None, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_dict_entries():
    testdict = {'pre': [{'a': i, 'b': j} for i in range(3) for j in range(3)],
                'post': [{'c': k, 'd': l} for k in range(3) for l in range(3)]}
    expdf = pd.DataFrame({('pre', 'a'): [0, 0, 0, 1, 1, 1, 2, 2, 2],
                          ('pre', 'b'): [0, 1, 2, 0, 1, 2, 0, 1, 2],
                          ('post', 'c'): [0, 0, 0, 1, 1, 1, 2, 2, 2],
                          ('post', 'd'): [0, 1, 2, 0, 1, 2, 0, 1, 2]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_list_and_str():
    testdict = {'a': [['c', 'd'], 'esr']}
    expdf = pd.DataFrame({('a', 0): ['c', 'esr'],
                          ('a', 1): ['d', None]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_dict_and_str():
    testdict = {'pre': [{'a': 'b'}, 'string']}
    expdf = pd.DataFrame({('pre', 0): [None, 'string'],
                          ('pre', 'a'): ['b', None]})
    frame = multilevel_dataframe(testdict)
    print(frame)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_dict_and_list():
    testdict = {'b': [{'a': 10}, [1, 2, 3]]}
    expdf = pd.DataFrame({('b', 'a'): [10, None],
                          ('b', 0): [None, 1],
                          ('b', 1): [None, 2],
                          ('b', 2): [None, 3]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_columns_different_levels():
    testdict = {'b': [{'a': 1}],
                'c': ['d']}
    expdf = pd.DataFrame({('b', 'a'): [1],
                          ('c', ''): ['d']})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_nested_dicts_and_lists():
    testdict = {'a': [{'b': [1, 2]}]}
    expdf = pd.DataFrame({('a', 'b', 0): [1],
                          ('a', 'b', 1): [2]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_deeply_nested():
    testdict = {'param': [{'value': [1, 2],
                           'exclude': {'value': 2, 'exclude': [4, 5, 6]}}]}

    expdf = pd.DataFrame({('param', 'value', 0, ''): [1],
                          ('param', 'value', 1, ''): [2],
                          ('param', 'exclude', 'value', ''): [2],
                          ('param', 'exclude', 'exclude', 0): [4],
                          ('param', 'exclude', 'exclude', 1): [5],
                          ('param', 'exclude', 'exclude', 2): [6]})
    frame = multilevel_dataframe(testdict)
    print(expdf, "\n\n", frame)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_many_different_levels():
    testdict = {'a': [{'b': [1, 2]}],
                'c': [3]}
    expdf = pd.DataFrame({
        ('a', 'b', 0): [1],
        ('a', 'b', 1): [2],
        ('c', '', ''): [3]})
    frame = multilevel_dataframe(testdict)
    print(expdf, "\n\n", frame)
    pdt.assert_frame_equal(expdf, frame)


@pyt.mark.xfail
def test_set():
    testdict = {'c': [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}]}
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_with_samples():
    """demonstrate basic usecase"""
    testdict = {'layer': ['L1', ['L2', 'L3'], 'L4', 'L5', 'L6'],
                'region': 'SSp-ll',
                'samples': [[1, 2, 3],
                            [4, 5, 6],
                            [2, 1, 1],
                            [1, 2, 3],
                            [3, 4, 1]]}
    expdf = pd.DataFrame({('layer', 0): ['L1', 'L2', 'L4', 'L5', 'L6'],
                          ('layer', 1): [None, 'L3', None, None, None],
                          ('region', ''): 'SSp-ll',
                          ('samples', 0): [1, 4, 2, 1, 3],
                          ('samples', 1): [2, 5, 1, 2, 4],
                          ('samples', 2): [3, 6, 1, 3, 1]})
    frame = multilevel_dataframe(testdict)
    print(expdf, "\n\n", frame)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_preserves_order():
    testdict = OrderedDict([
        ('g', [OrderedDict([('e', [2]),
                            ('f', [1])])]),
        ('a', [OrderedDict([('b', [1, 2])])]),
        ('c', [3])])
    expdf = pd.DataFrame(OrderedDict([
        (('g', 'e', 0), [2]),
        (('g', 'f', 0), [1]),
        (('a', 'b', 0), [1]),
        (('a', 'b', 1), [2]),
        (('c', '', ''), [3])]))

    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame)
