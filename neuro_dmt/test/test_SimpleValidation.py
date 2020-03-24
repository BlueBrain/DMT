import pandas as pd
from neuro_dmt.library.composition import SimpleValidation
import pytest as pyt


class TestSimpleValidation:

    class TestInitialzation:

        def test_checks_phenomenon(self):

            class TestValidation(SimpleValidation):
                def get_measurement(self, m, q):
                    pass
                pass

            with pyt.raises(ValueError):
                TestValidation()

        def test_sets_data(self):

            class TestValidation(SimpleValidation):
                phenomenon = "Test"
                def get_measurement(self, j, b):
                    pass
                pass

            data = pd.DataFrame({"buh": [1, 2, 3, 4]})
            assert all(TestValidation(data=data).data == data)
