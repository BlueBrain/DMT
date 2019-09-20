import pytest as pyt
from dmt.tk.terminology.parameters import Parameter, with_parameters, MissingParameterException


class Test_with_parameters:
    """test the decorator"""

    region = Parameter('region', 'a brain region')
    layer = Parameter('layer', 'some layer of a brain region')

    def test_parameters_present(self):
        @with_parameters(self.region, self.layer)
        def afuncof(region='lala', layer='lolo'):
            """
            Arguments: {parameters}
            """
            return region + layer

        assert afuncof.__doc__ ==\
            """
            Arguments: region: a brain region
                       layer: some layer of a brain region
            """

    def test_params_asterisk(self):
        @with_parameters(self.region, self.layer)
        def kwargyparams(**parameters):
            """
            a docstring for:
                {parameters}
            """
            return parameters
        assert kwargyparams.__doc__ ==\
            """
            a docstring for:
                region: a brain region
                layer: some layer of a brain region
            """

    def test_params_missing(self):
        with pyt.raises(MissingParameterException):
            @with_parameters(self.layer)
            def missingparams(blorgl=None):
                """...{parameters}"""
                return None
