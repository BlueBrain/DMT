# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

import pytest as pyt
from dmt.tk import terminology


class tparams():
    region = terminology.Term('region', 'a brain region')
    layer = terminology.Term('layer', 'some layer of a brain region')


class Test_use:
    """test the decorator"""

    def test_documentation_with_stripping(self):
        """
        A method decorated with `terminology.use` should have the
        expected documentation, with whitespace stripped.
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

    def test_documentation_with_formatting(self):
        """
        A method decorated with `terminology.use` should have the
        expected documentation, and the docstring should be well formatted,
        to the extend that it respects the expected whitespace.

        Add extensive edge-cases below to make sure that the `terminology`
        decorators produce good docstrings.
        """
        @terminology.use(tparams.region, tparams.layer)
        def get_region_layer(region, layer):
            """
            Get a layer region acronym.
            Arguments: {parameters}
            """
            pass

        doc_observed = get_region_layer.__doc__
        doc_expected =\
            """
            Get a layer region acronym.
            Arguments: region: a brain region
                       layer: some layer of a brain region
            """
        assert doc_observed  == doc_expected,\
            """
            Observed: {}
            Expected: {}
            """.format(
                doc_observed,
                doc_expected)

    def test_documentation(self):
        """
        A method decorated with `terminology.use` should have the
        expected documentation.
        """
        self.test_documentation_with_formatting()


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
        Raise a `terminology.MissingTermError` if there are terms missing in the signature of a
        method decorated by `terminology.use`.
        """
        with pyt.raises(terminology.MissingTermError):
            @terminology.use(tparams.layer)
            def missingparams(region="SSp-ll"):
                """...{parameters}"""
                return region
        with pyt.raises(terminology.MissingTermError):
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

    def test_method_with_explicit_args(self):
        """
        A method that only take positional arguments, and
        decorated with `terminology.use` should behave like as if there
        was no decoration except that of their doc-string.
        """
        def get_region_layer(region, layer='default'):
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
        assert doc_observed == doc_expected,\
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

        with pyt.raises(TypeError) as decorated_error:
            decorated(layer='v')
        with pyt.raises(TypeError) as naked_error:
            get_region_layer(layer='v')
        assert str(decorated_error.value) == str(naked_error.value)

        with pyt.raises(TypeError) as decorated_error:
            decorated()
        with pyt.raises(TypeError) as naked_error:
            get_region_layer()
        assert str(decorated_error.value) == str(naked_error.value)

    def test_unexpected_varkwargs_key(self):
        """
        Unexpected key in var-kwargs should throw a terminology.MissingTermError.
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

        with pyt.raises(terminology.MissingTermError):
            get_layer_region(mtype="L23_MC")

        @terminology.use(tparams.region, tparams.layer)
        def get_layer_region(region="SSp-ll", nsamples=1, **kwargs):
            """{parameters}"""
            layer = kwargs.get("layer")
            layer_region = region if not layer\
                else "{};{}".format(region, layer)
            return "-".join(layer_region for _ in range(nsamples))

        with pyt.raises(terminology.MissingTermError):
            get_layer_region(mtype="L23_MC")

    def test_varkwargs(self):
        """
        Missing or unknown keyword arguments should raise terminology.MissingTermErrors.
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
        with pyt.raises(KeyError):
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
            return True

        return nodocfun("SSp-ll")

    def test_wraps_keyerrors(self):
        """
        if a decorated parameter is sought down the line and not found,
        (raises a KeyError), we should raise a terminology.MissingTermError at the upper level
        """

        def inner_func(adict):
            adict[tparams.region]
            adict.get(tparams.layer, 'value')

        @terminology.use(tparams.region, tparams.layer)
        def passes_varkwargs(**kwargs):
            inner_func(kwargs)

        # require region
        with pyt.raises(KeyError) as ke:
            passes_varkwargs()
            assert "are you sure" in str(ke.value)

        passes_varkwargs(region='v')

    def test_does_not_wrap_unrelated_keyerror(self):
        """
        some KeyErrors are not related to missing parameters
        these should not be wrapped
        """
        def _unrelated_kwarg(adict):
            adict['different']

        def _param_on_other_mappable(adict):
            {'a dict_lacking_region': 'v'}[tparams.region]

        @terminology.use(tparams.region)
        def passes_to_unrelated(**kwargs):
            _unrelated_kwarg(kwargs)

        @terminology.use(tparams.region)
        def passes_to_other_mappable(**kwargs):
            _param_on_other_mappable(kwargs)

        with pyt.raises(KeyError):
            passes_to_unrelated()

        with pyt.raises(KeyError):
            passes_to_other_mappable(region='value')


class Test_require():
    """
    Test `terminology.require`
    """
    def test_only_var_kwargs(self):
        """
        A method with only variable kwargs can be decorated to match
        the kwargs with a terminology.
        """
        @terminology.require(tparams.region, tparams.layer)
        def get_region_layer(**kwargs):
            """
            Get a layer region acronym.
            Arguments: {parameters}
            """
            x = kwargs[tparams.region]
            y = kwargs[tparams.layer]
            return "{};{}".format(x, y)

        with pyt.raises(terminology.MissingTermError):
            """
            A method defined as `get_region_layer` above has to be
            called with variable keyword arguments alone.
            """
            get_region_layer()
            get_region_layer("SSp-ll", "L1")

        with pyt.raises(terminology.MissingTermError):
            """
            The keywords used to call such a method must agree with the
            terminology declared in the decorator.
            """
            get_region_layer(area="SSp-ll", layer="L1")

        observed = get_region_layer(region="SSp-ll", layer="L1")
        expected = "SSp-ll;L1"
        assert observed  == expected, "{} != {}".format(observed, expected)

        # TODO: ensure consistent order
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




class Test_where():
    """
    Test decorating with `terminology.where`
    """

    def test_(self):
        """
        Test the declaration of terms used in a method.
        """
        @terminology.where(
            x=tparams.region,
            y=tparams.layer)
        def get_layer_region(x, y):
            """
            Demonstrate use of layer and region.
            """
            return "{};{}".format(x, y)

        assert get_layer_region("SSp-ll", "L1") == "SSp-ll;L1"

        with pyt.raises(TypeError):
            get_layer_region()
        with pyt.raises(TypeError):
            get_layer_region(region="V", nucleus="L1")

    def test_documentation(self):
        """
        A method decorated with `terminology.use` should have the
        expected documentation.
        """
        @terminology.where(
            x=tparams.region,
            y=tparams.layer)
        def get_region_layer(x, y):
            """
            Get a layer region acronym.
            Arguments: {parameters}
            """
            pass

        doc_observed = get_region_layer.__doc__.strip()
        doc_expected =\
            """
            Get a layer region acronym.
            Arguments: x: a brain region
                       y: some layer of a brain region
            """.strip()
        # TODO: preserve order
        assert doc_observed  == doc_expected,\
            """
            Observed: {}
            Expected: {}
            """.format(
                doc_observed,
                doc_expected)

    def test_argument_order(self):
        """
        Order of arguments may not match the order declared in
        `terminology.where`
        """
        @terminology.where(
            x=tparams.region,
            y=tparams.layer)
        def get_layer_region(y, x):
            """
            demonstrate use of layer and region.
            """
            return "{};{}".format(x, y)

        observed = get_layer_region("L1", "SSp-ll")
        expected = "SSp-ll;L1"
        assert observed  == expected, "{} != {}".format(observed, expected)

        @terminology.where(
            x=tparams.region,
            y=tparams.layer)
        def get_layer_region(x, y):
            """
            demonstrate use of layer and region.
            """
            return "{};{}".format(x, y)

        observed = get_layer_region("SSp-ll", "L1")
        expected = "SSp-ll;L1"
        assert observed  == expected, "{} != {}".format(observed, expected)

        observed = get_layer_region(x="SSp-ll", y="L1")
        expected = "SSp-ll;L1"
        assert observed  == expected, "{} != {}".format(observed, expected)

    def test_only_var_kwargs(self):
        """
        A method with only variable kwargs can be decorated to match
        the kwargs with a terminology.
        """
        @terminology.where(
            region=tparams.region,
            layer=tparams.layer)
        def get_region_layer(**kwargs):
            """
                Get a layer region acronym.
                Arguments: {parameters}
                """
            x = kwargs[tparams.region]
            y = kwargs[tparams.layer]
            return "{};{}".format(x, y)

        with pyt.raises(terminology.MissingTermError):
            """
            A method defined as `get_region_layer` above has to be
            called with variable keyword arguments alone.
            """
            get_region_layer()
            get_region_layer("SSp-ll", "L1")

        with pyt.raises(terminology.MissingTermError):
            """
            The keywords used to call such a method must agree with the
            terminology declared in the decorator.
            """
            get_region_layer(area="SSp-ll", layer="L1")

        observed = get_region_layer(region="SSp-ll", layer="L1")
        expected = "SSp-ll;L1"
        assert observed  == expected, "{} != {}".format(observed, expected)



    def test_no_var_args_kwargs(self):
        """
        Cannot use variable args and kwargs with `terminology.where`
        """
        with pyt.raises(TypeError):
            @terminology.where(
                x=tparams.region,
                y=tparams.layer)
            def get_region_layer(x, y, *args):
                """
                Get a layer region acronym.
                Arguments: {parameters}
                """
                pass

        with pyt.raises(TypeError):
            @terminology.where(
                x=tparams.region,
                y=tparams.layer)
            def get_region_layer(x, y, **kwargs):
                """
                Get a layer region acronym.
                Arguments: {parameters}
                """
                pass

        with pyt.raises(TypeError):
            @terminology.where(
                x=tparams.region,
                y=tparams.layer)
            def get_region_layer(x, y, *args, **kwargs):
                """
                Get a layer region acronym.
                Arguments: {parameters}
                """
                pass
