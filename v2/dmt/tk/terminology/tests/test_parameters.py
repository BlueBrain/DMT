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

    def test_empty_docstring(self):
        """
        Decorator should provide a docstring even if the original method
        lacks one.
        """
        @terminology.use(tparams.region)
        def nodocfun(region='v', idonthaveadocstring="whatchugonnadoaboutit?"):
            return None
        assert nodocfun.__doc__ == \
            ("Arguments:\n"
             "    region: a brain region")

    def test_missing_params_in_signature(self):
        """
        Raise a `TypeError` if there are terms missing in the signature of a
        method decorated by `terminology.use`.
        """
        with pyt.raises(TypeError):
            @terminology.use(tparams.layer)
            def missingparams(region="SSp-ll"):
                """...{parameters}"""
                return region
        with pyt.raises(TypeError):
            @terminology.use(tparams.layer)
            def missingparams(region):
                """...{parameters}"""
                return region

    def test_positional_args(self):
        """
        Pass positional arguments or keyword arguments to a decorated method.
        """
        @terminology.use(tparams.region)
        def afuncof(region):
            """
            Arguments: {arguments}
            """
            return region

        assert afuncof("region") == "region"
        assert afuncof(region="region") == "region"

    def test_method_with_only_positional_args(self):
        """
        A method that only take positional arguments, and
        decorated with `terminology.use` should behave like as if there
        was no decoration except that of their doc-string.
        """
        def get_region_layer(region, layer):
            """
            Get a layer region acronym.
            Arguments: {parameters}
            """
            return "{};{}".format(region, layer)

        decorated = terminology.use(
            tparams.region, tparams.layer)(
                get_region_layer)

        doc_observed = decorated.__doc__.strip()
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
        assert get_region_layer("SSp-ll", "L1") == decorated("SSp-ll", "L1")

        with pyt.raises(TypeError) as decorated_error:
            decorated("SSp-ll", "L1", "L23_MC")
        with pyt.raises(TypeError) as naked_error:
            get_region_layer("SSp-ll", "L1", "L23_MC")
        assert str(decorated_error.value) == str(naked_error.value)

        with pyt.raises(TypeError) as decorated_error:
            decorated("SSp-ll", "L1", mtype="L23_MC")
        with pyt.raises(TypeError) as naked_error:
            get_region_layer("SSp-ll", "L1", mtype="L23_MC")
        assert str(decorated_error.value) == str(naked_error.value)

    def test_unexpected_varkwargs_key(self):
        """
        Unexpected key in var-kwargs should throw a TypeError.
        """
        @terminology.use(tparams.region, tparams.layer)
        def get_layer_region(**kwargs):
            """
            a docstring for:
                {parameters}
            """
            region = kwargs[tparams.region]
            layer = kwargs[tparams.layer]
            return "{};{}".format(region, layer)

        with pyt.raises(TypeError):
            get_layer_region(mtype="L23_MC")

        @terminology.use(tparams.region, tparams.layer)
        def get_layer_region(region="SSp-ll", nsamples=1, **kwargs):
            """{parameters}"""
            layer = kwargs.get("layer")
            layer_region = region if not layer\
                else "{};{}".format(region, layer)
            return "-".join(layer_region for _ in range(nsamples))

        with pyt.raises(TypeError):
            get_layer_region(mtype="L23_MC")

    def test_varkwargs(self):
        """
        Missing or unknown keyword arguments should raise TypeErrors.
        """
        @terminology.use(tparams.region, tparams.layer)
        def get_layer_region(**kwargs):
            """
            a docstring for:
                {parameters}
            """
            region = kwargs[tparams.region]
            layer = kwargs[tparams.layer]
            return "{};{}".format(region, layer)

        assert get_layer_region(region="SSp-ll", layer="L1") == "SSp-ll;L1"
        with pyt.raises(TypeError):
            get_layer_region()

    def test_kwargs_and_varkwargs(self):
        """
        A method with explicit kwargs and var-kwargs can be decorated.
        """
        @terminology.use(tparams.region, tparams.layer)
        def get_layer_region(region="SSp-ll", nsamples=1, **kwargs):
            """{parameters}"""
            layer = kwargs.get("layer")
            layer_region = region if not layer\
                else "{};{}".format(region, layer)
            return "-".join(layer_region for _ in range(nsamples))

        assert get_layer_region() == "SSp-ll"
        observed_2 = get_layer_region(region='SSp-hl', nsamples=2, layer="L2")
        assert observed_2 == "SSp-hl;L2-SSp-hl;L2", observed_2

    def unformattable_docstring(self):
        """
        if {parameters} is not in the docstring, what do we do?
        """
        @terminology.use(tparams.region)
        def nodocfun(region):
            """no params here"""
            return None


