# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop a document builder.
"""
import inspect
from collections import OrderedDict
from pathlib import Path
from dmt.tk.field import NA, Record
from dmt.tk.journal import Logger
from ..components import *
from ..builder import *
from .import test_composition
from .test_composition import *
from .import *

"""
TODO: The author of a document should enter the content as methods.
What should the arguments of these methods be?


In literate programming, code is embedded into written language.
With Python, we can leverage doc-strings to embed written language
part of a document into Python code.
A narrative should be added as the doc-string.
In this case this doc-string will appear in the abstract.
"""
LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def test_context_management():
    """Test context management functionality of `DocumentBuilder`"""

    adapter = MockAdapter()
    model = MockModel()
    path_save = get_path_save().joinpath("context")
    path_save.mkdir(parents=False, exist_ok=True)

    with DocumentBuilder("Test") as document:
        assert document.title == "Test"
        assert document.abstract.document_builder == document

        report = Document("Test")

        @document.abstract
        def _():
            """
            We analyze the densities of cortical layers \\model{layer_values}
            """
            pass

        assert document.abstract.content
        assert '_' in document.abstract.content
        abstract = document.abstract.get(report)
        value_abstract = abstract(adapter, model)
        path_abstract = abstract.save(value_abstract, path_save)
        test_abstract(Record(
            abstract=abstract,
            value=value_abstract,
            path_save=path_save))

        @document.introduction
        def _():
            """
            Cortical area such as the \model{brain_region} is composed of layers of cells with different cell densities. In this report we analyze circuit composition of cortical layers \model{layer_values}, focusing on total cell density and the fraction of inhibitory neurons in each layer. In our model of the \model{brain_region} we have reconstructed the sub-regions \model{sub_brain_regions}. Experimental measurements for cell densities for these sub-regions were not available. Hence we have used the same cell densities presented in the figure for each of the these regions.
            """
            pass

        @document.introduction.illustration
        def neocortical_scaffold():
            """
            The neocortex is a 2-3 mm thick sheet of tissue on the surface of the brain. The figure above shows a digitally reconstructed neocortical column.
            """
            return Path(os.getcwd()).joinpath(
                "resources/neocortical_scaffold.png")

        assert document.introduction.content.narrative
        assert "_" in document.introduction.content.narrative
        assert document.introduction.illustration

        introduction = document.introduction.get(report)
        value_introduction = introduction(adapter, model)
        path_introduction = introduction.save(value_introduction, path_save)
        test_introduction(Record(
            introduction=introduction,
            value=value_introduction,
            path_save=path_save))

        @document.methods
        def _():
            """
            Random cell densities were assigned to each pair of (sub-region, layer) for sub-regions \\model{sub_brain_regions} and layers \\model{layer_values}, for the purposes of mocking the behavior of a `methods` instance.
            """
            pass

        @document.methods.reference_data
        def cell_density():
            """
            Experimentally measured cell density data.
            """
            return CompositeData({
                "abcYYYY": mock_reference_data_cell_density(),
                "uvwXXXX": mock_reference_data_cell_density()})
        @document.methods.reference_data
        def inhibitory_fraction():
            """
            Experimentally measured fraction of inhibitory cells.
            """
            return CompositeData({
                "abcYYYY": mock_reference_data_inhibitory_fraction(),
                "uvwXXXX": mock_reference_data_inhibitory_fraction()})
        @interfacemethod
        def get_brain_regions(adapter, model):
            """
            The `adapter` should implement a method to get brain regions that were
            reconstructed in the given `model`
            """
            raise NotImplementedError
        
        @interfacemethod
        def get_layers(adapter, model):
            """
            The `adapter` should implement a method to names used for the layers
            of brain region that were reconstructed in the given `model`.
            """
            raise NotImplementedError
        
        def regions_and_layers(adapter, model, *args, **kwargs):
            """..."""
            regions = adapter.get_brain_regions(model)
            layers = adapter.get_layers(model)
            return pd.DataFrame(
                [[r, l] for r in regions for l in layers],
                columns=["region", "layer"])
        
        @document.methods.measurements
        def cell_density():
            """
            Layer cell densities for regions \\model{sub_brain_regions}.
            """
            def _cell_density(adapter, model, **query):
                layer = query["layer"]
                region = query["region"]
                return\
                    mock_cell_density_values.loc[(region, layer)]\
                                            .sample(n=1)\
                                            .iloc[0]\
                                            .cell_density
            return dict(
                description="""
                Layer cell densities for regions \\model{sub_brain_regions}.
                """,
                parameters=regions_and_layers,
                method=_cell_density,
                sample_size=20)

        @document.methods.measurements
        def inhibitory_fraction():
            """
            Layer inhibitory cell fractions for regions \\model{sub_brain_regions}.
            """
            def _inhibitory_fraction(adapter, model, **query):
                layer = query["layer"]
                region = query["region"]
                return\
                    mock_inh_fraction_values.loc[(region, layer)]\
                                            .sample(n=1)\
                                            .iloc[0]\
                                            .inhibitory_fraction
            return dict(
                description="""
                Layer inhibitory cell fractions for regions \\model{sub_brain_regions}.
                """,
                parameters=regions_and_layers,
                method=_inhibitory_fraction,
                sample_size=20)
        
        methods = document.methods.get(report)
        test_composition._test_methods_instance(methods, adapter, model)

        value_methods = methods(adapter, model)

        test_composition._test_methods_value(value_methods, adapter, model)
        path_methods = methods.save(value_methods, path_save)
        test_methods(Record(
            methods=methods,
            value=value_methods,
            path_save=path_save))

        report.methods = methods

        @document.results
        def _():
            """
            Random cell densities were assigned to each pair of
            (sub-region, layer) for sub-regions \\model{sub_brain_regions}
            and layers \\model{layer_values}, for the purposes of mocking the
            behavior of a `methods` instance.
            """
            pass


        @document.results.illustration
        def cell_density():
            """
            Mock cell density for a cortical circuit.
            """
            return MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer", xlabel="Layer",
                    yvar="cell_density", ylabel="Cell Density",
                gvar="dataset"))

        @document.results.illustration
        def inhibitory_fraction():
            """
            Mock inhibitory fraction for a cortical circuit.
            """
            return MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer", xlabel="Layer",
                    yvar="inhibitory_fraction", ylabel="Inhibitory Fraction",
                    gvar="dataset"))

        results = document.results.get(report)
        test_composition._test_results_instance(results, adapter, model)

        value_results = results(adapter, model)

        test_composition._test_results_value(value_results, adapter, model)
        path_results = results.save(value_results, path_save)
        test_results(Record(
            results=results,
            value=value_results,
            path_save=path_save))

