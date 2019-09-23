import pytest as pyt
from dmt.tk import terminology


class tparams():
    region = terminology.Term('region', 'a brain region')
    layer = terminology.Term('layer', 'some layer of a brain region')


class Test_use:
    """test the decorator"""

    def test_documentation(self):
        """
        A method decorated with `terminology.use` should have the
        expected documentation.
        """
        @terminology.use(tparams.region, tparams.layer)
        def get_region_layer(region, layer):
            """
            Get a layer region acronym.
            Arguments: {parameters}
            """
            pass

        doc_observed = get_region_layer.__doc__.strip()
        doc_expected =\
            """
            Get a layer region acronym.
            Arguments: region: a brain region
                       layer: some layer of a brain region
            """.strip()
        assert doc_observed  == doc_expected,\
            """
            Observed: {}
            Expected: {}
            """.format(
                doc_observed,
                doc_expected)


    def test_parameters_present(self):
        """
        if all arguments are present, the docstring should be amended
        and the method should otherwise work as normal
        """
        def afuncof(region='lala', layer='lolo', different=''):
            """
            Arguments: {parameters}
            """
            return region + layer + different

        decorated = terminology.use(tparams.region, tparams.layer)(afuncof)

        assert decorated() == 'lalalolo'
        assert decorated(region="a region", layer="a layer")\
            == "a regiona layer"
        assert decorated(different='. yep.') == 'lalalolo. yep.'

        with pyt.raises(TypeError) as e:
            decorated(otherkwarg='a value')

        with pyt.raises(TypeError) as unwrapped_e:
            afuncof(otherkwarg='a value')

        assert str(e.value) == str(unwrapped_e.value)

    def test_params_asterisk(self):
        """
        **-like parameters in principle satisfy any kwargs
        """
        @terminology.use(tparams.region, tparams.layer)
        def varkwargyparams(**parameters):
            """
            a docstring for:
                {parameters}
            """
            return parameters

        assert varkwargyparams() == {}
        assert varkwargyparams(region="a region", layer="a layer") ==\
            {'region': 'a region', 'layer': 'a layer'}
        with pyt.raises(TypeError):
            varkwargyparams(blr='blr')

    def test_kwargs_and_varkwargs(self):
        """
        test that this works smoothly for methods with both
        explicit kwargs and varkwargs
        """
        @terminology.use(tparams.region, tparams.layer)
        def kwargsandvarkwargs(region='', nsamples=1, **kwargs):
            """{parameters}"""
            return
        kwargsandvarkwargs()
        kwargsandvarkwargs(region='dsasad', nsamples=100, layer='')
        with pyt.raises(TypeError):
            kwargsandvarkwargs(blah='')

    def test_params_missing(self):
        """
        if some parameter in the decorator is not defined for the method
        an exception should be raised
        """
        with pyt.raises(TypeError):
            @terminology.use(tparams.layer)
            def missingparams(blorgl=None):
                """...{parameters}"""
                return None

    def test_positional_args(self):
        """
        positional arguments can be passed to with = just like kwargs can
        so they can qualify if they have the right name
        """
        @terminology.use(tparams.region)
        def afuncof(region):
            """
            Arguments: {arguments}
            """
            return region

        assert afuncof("region") == "region"

    def unformattable_docstring(self):
        """
        if {parameters} is not in the docstring, what do we do?
        """
        @terminology.use(tparams.region)
        def nodocfun(region):
            """no params here"""
            return None

    def test_empty_docstring(self):
        """
        if there is no docstring, what do we do?
        """
        @terminology.use(tparams.region)
        def nodocfun(region='v', idonthaveadocstring="whatchugonnadoaboutit?"):
            return None
        assert nodocfun.__doc__ == \
            ("Arguments:\n"
             "    region: a brain region")

