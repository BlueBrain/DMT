import pandas as pd
from dmt.tk.plotting.utils import make_hashable


# TODO: dicts and strings
class TestMakeHashable:

    def test_given_strings(self):
        tdf = pd.DataFrame(dict(pre=['a', 'b', 'c', 'd']))
        df, label = make_hashable(tdf,  'pre')
        pd.testing.assert_frame_equal(df, tdf)
        assert label == 'pre'

    def test_given_dicts(self):
        tdf = pd.DataFrame(dict(pre=[
            {'layer': l, 'mtype': m}
            for l, m in enumerate(['a' 'b', 'c', 'd'])]))
        df, label = make_hashable(tdf,  'pre')

        edf = pd.DataFrame({'pre: layer, mtype':
                            [str(l) + ", " + str(m)
                             for l, m in enumerate(['a' 'b', 'c', 'd'])]})

        pd.testing.assert_frame_equal(df, edf)
        assert label == edf.columns[0]

    def test_mismatched_dicts(self):
        tdf = pd.DataFrame({
            'buh': [{'mtype': 'a', 'layer': '1'},
                    {'layer': '3'},
                    {'mtype': 'b', 'layer': '2'},
                    {'mtype': 'c', 'layer': '3', 'unnecessary': 'detail'}]})
        edf = pd.DataFrame({
            'buh: layer, mtype, unnecessary': [
                '1, a, _',
                '3, _, _',
                '2, b, _',
                '3, c, detail']})
        df, label = make_hashable(tdf, 'buh')
        pd.testing.assert_frame_equal(df, edf)
