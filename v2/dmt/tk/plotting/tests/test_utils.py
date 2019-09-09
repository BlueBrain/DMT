import pandas as pd
from collections import OrderedDict
from dmt.tk.plotting.utils import make_hashable


# TODO: dicts and strings
class TestMakeHashable:

    def test_given_strings(self):
        tdf = pd.DataFrame(dict(pre=['a', 'b', 'c', 'd']))
        df, label = make_hashable(tdf,  'pre')
        pd.testing.assert_frame_equal(df, tdf)
        assert label == 'pre'

    def test_given_dicts(self):
        tdf = pd.DataFrame(OrderedDict(
            [(('pre', 'layer'), range(4)),
             (('pre', 'mtype'), ['a', 'b', 'c', 'd'])]))
        df, label = make_hashable(tdf,  'pre')

        edf = pd.DataFrame({('pre: layer, mtype', ''):
                            [str(l) + ", " + str(m)
                             for l, m in enumerate(['a', 'b', 'c', 'd'])]})
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
        assert label == 'pre: layer, mtype'

    def test_mismatched_dicts(self):
        tdf = pd.DataFrame(OrderedDict([
            (('buh', 'layer'), ['1', '3', '2', '3']),
            (('buh', 'mtype'), ['a', None, 'b', 'c']),
            (('buh', 'unecessary'), [None, None, None, 'detail'])]))

        edf = pd.DataFrame({
            ('buh: layer, mtype, unecessary', ''): [
                '1, a, _',
                '3, _, _',
                '2, b, _',
                '3, c, detail']})
        df, label = make_hashable(tdf, 'buh')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)

    def test_deeper(self):
        tdf = pd.DataFrame(OrderedDict([
            (('a', 'b', 'c'), [1, 2, 3]),
            (('a', 'b', 'd'), [1, 3, 4]),
            (('a', 'c', 'g'), [2, 3, 4])]))
        edf = pd.DataFrame({
            ('a: {b: {c, d}, c: g}', '', ''):
            ['1, 1, 2', '2, 3, 3', '3, 4, 4']})
        df, label = make_hashable(tdf, 'a')
        print(df, "\n\n", edf)
        pd.testing.assert_frame_equal(df, edf)
