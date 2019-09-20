import pytest as pyt
from dmt.tk.terminology.parameters import Parameter, with_parameters, MissingParameterException


class tparams():
    region = Parameter('region', 'a brain region')
    layer = Parameter('layer', 'some layer of a brain region')


class Test_with_parameters:
    """test the decorator"""

    def test_parameters_present(self):
        """
        if all arguments are present, the docstring should be amended
        and the method should otherwise work as normal
        """
        @with_parameters(tparams.region, tparams.layer)
        def afuncof(region='lala', layer='lolo', different=''):
            """
            Arguments: {parameters}
            """
            return region + layer + different

        assert afuncof.__doc__ ==\
            """
            Arguments: region: a brain region
                       layer: some layer of a brain region
            """
        assert afuncof() == 'lalalolo'
        assert afuncof(region="a region", layer="a layer") == "a regiona layer"
        assert afuncof(different='. yep.') == 'lalalolo. yep.'
        with pyt.raises(TypeError) as e:
            afuncof(otherkwarg='a value')
        with pyt.raises(TypeError) as unwrapped_e:
            def afuncof(region='lala', layer='lolo', different=''):
                """
                Arguments: {parameters}
                """
                return region + layer + different
            afuncof(otherkwarg='a value')

        assert str(e.value) == str(unwrapped_e.value)

    def test_params_asterisk(self):
        """
        **-like parameters in principle satisfy any kwargs
        """
        @with_parameters(tparams.region, tparams.layer)
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
        assert kwargyparams() == {}
        assert kwargyparams(region="a region", layer="a layer") ==\
            {'region': 'a region', 'layer': 'a layer'}
        assert kwargyparams(blr='blr') == {'blr': 'blr'}

    def test_params_missing(self):
        """
        if some parameter in the decorator is not defined for the method
        an exception should be raised
        """
        with pyt.raises(MissingParameterException):
            @with_parameters(tparams.layer)
            def missingparams(blorgl=None):
                """...{parameters}"""
                return None

    def test_positional_args(self):
        """
        positional arguments can be passed to with = just like kwargs can
        so they can qualify if they have the right name
        """
        @with_parameters(tparams.region)
        def afuncof(region):
            """
            Arguments: {parameters}
            """
            return region

        assert afuncof("region") == "region"

    def unformattable_docstring(self):
        """
        if {parameters} is not in the docstring, what do we do?
        """
        @with_parameters(tparams.region)
        def nodocfun(region):
            """no params here"""
            return None
        assert nodocfun.__doc__ ==\
            ("no params here\n"
             "Parameters:\n"
             "    region: a brain region")

    def test_empty_docstring(self):
        """
        if there is no docstring, what do we do?
        """
        @with_parameters(tparams.region)
        def nodocfun(region='v', idonthaveadocstring="whatchugonnadoaboutit?"):
            return None
        assert nodocfun.__doc__ == \
            ("Parameters:\n"
             "    region: a brain region")
