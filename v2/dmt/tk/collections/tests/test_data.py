import pytest as pyt
import pandas as pd
from pandas import testing as pdt
from collections import OrderedDict
from dmt.tk.collections.data import multilevel_dataframe


def test_plain_dict():
    """test that an ordinary dict just returns a pandas dataframe"""
    testdict = {'a': [1, 2, 3, 4], 'b': 0}
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_of_dict():
    """an un-nested list of dicts should just initialize a dataframe"""
    testdict = [{'a': 1, 'b': 0}, {'a': 2, 'b': 0}, {'a': 3}]
    expdf = pd.DataFrame(testdict)
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_entries():
    """
    when column elements are lists, this is resolved by creating
    a subcolumn for each element of the list
    c
    0 1 2
    """
    testdict = {'c': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_dicts_list():
    """
    when column elements are lists, this is resolved by creating
    a subcolumn for each element of the list
    c
    0 1 2
    """
    testdict = [{'c': a} for a in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_list_and_scalar():
    """
    if there are lists and scalars in the same column,
    the scalars should be treated as length-1 lists
    """
    testdict = {'c': [[1, 2, 3], 5, [7, 8, 9]]}
    expdf = pd.DataFrame({('c', 0): [1, 5, 7], ('c', 1): [2, None, 8],
                          ('c', 2): [3, None, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_dict_entries():
    """
    when column elements are dicts, this is resolved by creating a
    subcolumn for every key in the dicts
    pre  post
    a b  c d
    """
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
    """
    test that strings aren't interpreted as iterables
    when sharing a column with lists
    """
    testdict = {'a': [['c', 'd'], 'esr']}
    expdf = pd.DataFrame({('a', 0): ['c', 'esr'],
                          ('a', 1): ['d', None]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_dict_and_str():
    """
    when dict and string(or other scalars) are contained in the
    same column, the scalar should be interpreted as a length-1
    list, and hence stored in the 0 subcolumn
    """
    testdict = {'pre': [{'a': 'b'}, 'string']}
    expdf = pd.DataFrame({('pre', 0): [None, 'string'],
                          ('pre', 'a'): ['b', None]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_dict_and_list():
    """
    when the column contains list and dict together,
    this is resolved by creating both integer and string
    subcolumns, filling the cells that do not apply with None
    """
    testdict = {'b': [{'a': 10}, [1, 2, 3]]}
    expdf = pd.DataFrame({('b', 'a'): [10, None],
                          ('b', 0): [None, 1],
                          ('b', 1): [None, 2],
                          ('b', 2): [None, 3]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_columns_different_levels():
    """
    when different columns have different subcolumn-depths
    the shallower columns should still be straightforwardly
    indexable.
    """
    testdict = {'b': [{'a': 1}],
                'c': ['d']}
    expdf = pd.DataFrame({('b', 'a'): [1],
                          ('c', ''): ['d']})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_nested_dicts_and_lists():
    """
    All this should work on nested dicts and lists
    """
    testdict = {'a': [{'b': [1, 2]}]}
    expdf = pd.DataFrame({('a', 'b', 0): [1],
                          ('a', 'b', 1): [2]})
    frame = multilevel_dataframe(testdict)
    pdt.assert_frame_equal(expdf, frame,
                           check_like=True)


def test_deeply_nested():
    """
    and deeply nested ones, within reason
    """
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
    """
    two-level difference in the depth of nested dicts
    and lists should be resolved the same way as a
    one-level difference.
    """
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
    """presently, converting sets is not supported"""
    testdict = {'c': [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}]}
    expdf = pd.DataFrame({('c', 0): [1, 4, 7], ('c', 1): [2, 5, 8],
                          ('c', 2): [3, 6, 9]})
    pdt.assert_frame_equal(expdf, multilevel_dataframe(testdict),
                           check_like=True)


def test_with_samples():
    """demonstrate example usecase"""
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
    """
    when fed an OrderedDict, the order of columns should be the
    same as the order of keys in the OrderedDict
    """
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