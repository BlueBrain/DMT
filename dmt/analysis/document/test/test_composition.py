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
Test develop composition of Narrative, Data, Illustration
"""

from ..components import *
from ...measurement import CompositeData
from .import *

def get_abstract(document=None):
    kwargs = dict(
        narrative="""
        We analyze the densities of cortical layers \\model{layer_values}
        """)
    if document:
        kwargs["parent"] = document
        return Abstract(**kwargs)
    return kwargs

def _test_abstract_instance(abstract, adapter, model):
    """..."""
    assert isinstance(abstract, Abstract)
    assert hasattr(abstract, "narrative")
    assert abstract.narrative
    return True

def _test_abstract_value(value_abstract, adapter, model):
    assert value_abstract.title == "Abstract", value_abstract
    assert value_abstract.label == "abstract", value_abstract
    assert value_abstract.narrative.strip().startswith(
        "We analyze the densities of cortical layers"
    ), value_abstract.narrative.strip()

    for l in adapter.get_layers(model):
        assert l in value_abstract.narrative, value_abstract

    return True

def _test_abstract_save(path_save, abstract, model):
    path_abstract = path_save.joinpath("abstract")
    assert os.path.isfile(path_abstract.joinpath("narrative.txt"))
    return True

def test_abstract(test_object = None):
    """
    An `Abstract` should:
    1. have a title
    2. have a label
    3. have a narrative
    """
    adapter = MockAdapter()
    model = MockModel()
    if not test_object:
        document = Document("Test")
        abstract = get_abstract(document)
        _test_abstract_instance(abstract, adapter, model)
        value = abstract(adapter, model)
        _test_abstract_value(value, adapter, model)

        path_save = get_path_save()
        abstract.save(value, path_save)
        _test_abstract_save(path_save, abstract, model)
    else:
        try:
            abstract = test_object.abstract
        except AttributeError:
            abstract = test_object
        _test_abstract_instance(abstract, adapter, model)

        try:
            value = test_object.value_abstract
        except AttributeError:
            value = abstract(adapter, model)
        _test_abstract_value(value, adapter, model)

        try:
            path_save = test_object.path_save
        except AttributeError:
            path_save = get_path_save()
            abstract.save(value, path_save)
        _test_abstract_save(path_save, abstract, model)
    return True

def get_introduction(document=None):
    mock_experimental_figures = Bars(
        xvar="layer", xlabel="Layer",
        yvar="cell_density", ylabel="Cell Density"
    )(mock_cell_density())
    mock_experimental_figures.update(Bars(
        xvar="layer", xlabel="Layer",
        yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"
    )(mock_inh_fraction()))

    kwargs = dict(
        narrative="""Cortical area such as the \model{brain_region} is composed of layers of cells with different cell densities. In this report we analyze circuit composition of cortical layers \model{layer_values}, focusing on total cell density and the fraction of inhibitory neurons in each layer. In our model of the \model{brain_region} we have reconstructed the sub-regions \model{sub_brain_regions}. Experimental measurements for cell densities for these sub-regions were not available. Hence we have used the same cell densities presented in the figure for each of the these regions.
        """,
        illustration=Record(
            figures=mock_experimental_figures,
            caption="""
            Experimentally measured cell densities used to reconstruct sub-regions \model{sub_brain_regions} of the \model{animal} \model{brain_region}.
            """))
    if document:
        kwargs["parent"] = document
        return Introduction(**kwargs)
    return kwargs

def _test_introduction_instance(introduction, adapter, model):
    """..."""
    assert isinstance(introduction, Introduction)
    assert hasattr(introduction, "narrative")
    assert introduction.narrative
    assert hasattr(introduction, "illustration")
    assert introduction.illustration
    return True

def _test_introduction_value(value, adapter, model):
    assert value.title == "Introduction", value.title
    assert value.label == "introduction", value.label
    assert value.illustration.caption.strip().startswith(
        "Experimentally measured"
    ), value.illustration.caption
    return True

def _test_introduction_save(path_save, adapter, model):
    path_introduction = path_save.joinpath("introduction")
    assert os.path.isfile(
        path_introduction.joinpath("narrative.txt"))

    path_illustration = path_introduction.joinpath("illustration")
    assert os.path.exists(
        path_illustration)
    assert os.path.isfile(
        path_illustration.joinpath("cell_density.png"))
    assert os.path.isfile(
        path_illustration.joinpath("inhibitory_fraction.png"))
    return True

def test_introduction(test_object=None):
    """
    An `Introduction`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. may have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()

    if not test_object:
        document = Document("Test")
        introduction = get_introduction(document)
        _test_introduction_instance(introduction, adapter, model)

        value = introduction(adapter, model)
        _test_introduction_value(value, adapter, model)

        path_save = get_path_save()
        introduction.save(value, path_save)
        _test_introduction_save(path_save, adapter, model)
    else:
        try:
            introduction = test_object.introduction
        except AttributeError:
            introduction = test_object
        _test_introduction_instance(introduction, adapter, model)
        try:
            value = test_object.value_abstract
        except AttributeError:
            value = introduction(adapter, model)
        _test_introduction_value(value, adapter, model)
        try:
            path_save = test_object.path_save
        except AttributeError:
            path_save = get_path_save()
            introduction.save(value, path_save)
        _test_introduction_save(path_save, adapter, model)
    return True

def get_methods(document=None):
    kwargs_methods = dict(
        narrative="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `methods` instance.
        """,
        reference_data=CompositeData({
            "cell_density": CompositeData({
                "abcYYYY": mock_reference_data_cell_density(),
                "uvwXXXX": mock_reference_data_cell_density()}),
            "inhibitory_fraction": CompositeData({
                "abcYYYY": mock_reference_data_inhibitory_fraction(),
                "uvwXXXX": mock_reference_data_inhibitory_fraction()})}),
        measurements=OrderedDict([
            ("cell_density", {
                "description": """
                Layer cell densities for regions \\model{sub_brain_regions}.
                """,
                "parameters": regions_and_layers,
                "method": cell_density,
                "sample_size": 20}),
            ("inhibitory_fraction", {
                "description": """
                Layer inhibitory cell fractions for regions \\model{sub_brain_regions}.
                """,
                "parameters": regions_and_layers,
                "method": inhibitory_fraction,
                "sample_size": 20})]))
    if document:
        return Methods(parent=document,**kwargs_methods)
    return kwargs_methods

def _test_methods_instance(methods, adapter, model):
    """..."""
    assert isinstance(methods, Methods)
    assert hasattr(methods, "narrative")
    assert hasattr(methods, "measurements")
    assert isinstance(methods.measurements, MeasurementSuite)
    assert "cell_density" in methods.measurements
    assert "inhibitory_fraction" in methods.measurements
    return True

def _test_methods_value(value, adapter, model):
    """..."""
    assert value.title == "Methods"
    assert value.label == "methods"
    assert value.narrative.strip().startswith("Random cell densities")
    assert "cell_density" in value.measurements
    assert value.measurements["cell_density"].strip().startswith(
        "Layer cell densities")
    assert str(NA) not in value.measurements["cell_density"]
    assert "inhibitory_fraction" in value.measurements
    assert value.measurements["inhibitory_fraction"].strip().startswith(
        "Layer inhibitory cell fraction")
    assert str(NA) not in value.measurements["inhibitory_fraction"]

    assert hasattr(value, "reference_data")
    assert isinstance(value.reference_data, Mapping)
    assert "cell_density" in value.reference_data
    assert "inhibitory_fraction" in value.reference_data

def _test_methods_save(path_save, adapter, model):
    """..."""
    path_methods = path_save.joinpath("methods")
    assert os.path.exists(path_methods)
    assert os.path.isfile(path_methods.joinpath("narrative.txt"))
    assert os.path.isfile(path_methods.joinpath("measurements.json"))

    path_reference_data = path_methods.joinpath("reference_data")
    assert os.path.exists(path_reference_data)

    path_reference_data_cd = path_reference_data.joinpath("cell_density")
    assert os.path.exists(path_reference_data_cd)
    assert os.path.isfile(
        path_reference_data_cd.joinpath("abcYYYY.json"))
    assert os.path.isfile(
        path_reference_data_cd.joinpath("uvwXXXX.json"))

    path_reference_data_if = path_reference_data.joinpath("inhibitory_fraction")
    assert os.path.exists(path_reference_data_if)
    assert os.path.isfile(
        path_reference_data_if.joinpath("abcYYYY.json"))
    assert os.path.isfile(
        path_reference_data_if.joinpath("uvwXXXX.json"))
    return True

def test_methods(test_object=None):
    """
    Methods section of a document.

    On evaluation for (adapter, model):
    1. Narrative should be set.
    2. Only field description of each measurement should be evaluated,
    and set as the field `measurement` of the methods-value.

    Save `Methods` to
    1. write narrative into file "narrative.txt"
    2. write measurement label -> description to a "measurements.json"

    Note
    -------------------
    A `Method`'s measurements may contain entries that have either data or
    collector of data. These are not stored.
    Instead, we assume that some other object will handle the data associated
    with a `Methods` measurements.
    """
    adapter = MockAdapter()
    model = MockModel()

    if not test_object:
        document = Document("Test")
        methods = get_methods(document)
        _test_methods_instance(methods, adapter, model)

        value = methods(adapter, model)
        _test_methods_value(value, adapter, model)
    
        path_save=get_path_save()
        methods.save(value, path_save)
        _test_methods_save(path_save, adapter, model)
    else:
        try:
            methods = test_object.methods
        except AttributeError:
            methods = test_object
        _test_methods_instance(methods, adapter, model)

        try:
            value = test_object.value
        except AttributeError:
            value = methods(adapter, model)
        _test_methods_value(value, adapter, model)

        try:
            path_save = test_object.path_save
        except AttributeError:
            path_save = get_path_save()
            methods.save(value, path_save)
        _test_methods_save(path_save, adapter, model)
    return True

def get_results(document=None):
    plotter_cd = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density",
            gvar="dataset"))
    plotter_if = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction",
            gvar="dataset"))
    kwargs = dict(
        narrative="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `methods` instance.
        """,
        illustration=dict(
            figures=dict(
                cell_density=plotter_cd,
                inhibitory_fraction=plotter_if),
            caption="""Mock figures for the purpose of test developing `Results` do not deserved a caption.
            """))
            
    if document:
        return Results(parent=document, **kwargs)
    return kwargs

def _test_results_instance(results, adapter, model):
    """..."""
    assert results.title == "Results"
    assert results.label == "results"
    assert hasattr(results.parent, "methods")

    data_illustration = results.get_illustration_data(adapter, model)
    assert isinstance(data_illustration, Mapping)

    assert "cell_density" in data_illustration.keys()
    assert isinstance(data_illustration["cell_density"], Mapping)
    assert "MockModel" in data_illustration["cell_density"].keys()
    assert isinstance(
        data_illustration["cell_density"]["MockModel"],
        pd.DataFrame)
    assert "abcYYYY" in data_illustration["cell_density"].keys()
    assert isinstance(
        data_illustration["cell_density"]["abcYYYY"],
        pd.DataFrame)
    assert "uvwXXXX" in data_illustration["cell_density"].keys()
    assert isinstance(
        data_illustration["cell_density"]["uvwXXXX"],
        pd.DataFrame)

    assert "inhibitory_fraction" in data_illustration.keys()
    assert isinstance(data_illustration["inhibitory_fraction"], Mapping)
    assert "MockModel" in data_illustration["inhibitory_fraction"].keys()
    assert isinstance(
        data_illustration["inhibitory_fraction"]["MockModel"],
        pd.DataFrame)
    assert "abcYYYY" in data_illustration["inhibitory_fraction"].keys()
    assert isinstance(
        data_illustration["inhibitory_fraction"]["abcYYYY"],
        pd.DataFrame)
    assert "uvwXXXX" in data_illustration["inhibitory_fraction"].keys()
    assert isinstance(
        data_illustration["inhibitory_fraction"]["uvwXXXX"],
        pd.DataFrame)
    return True

def _test_results_value(value, adapter, model):
    """..."""
    assert value.label == "results"
    assert value.title == "Results"

    assert hasattr(value, "measurements")
    assert "cell_density" in value.measurements.keys()
    assert isinstance(value.measurements["cell_density"], pd.DataFrame)
    assert "inhibitory_fraction" in value.measurements.keys()
    assert isinstance(value.measurements["inhibitory_fraction"], pd.DataFrame)
    assert value.narrative.strip().startswith("Random cell densities")
    assert value.illustration.caption.strip().startswith("Mock figures")

    return True

def _test_results_save(path_save, adapter, model):
    """..."""
    path_results = path_save.joinpath("results")
    assert os.path.exists(path_results)
    assert os.path.isfile(path_results.joinpath("narrative.txt"))

    path_measurements = path_results.joinpath("measurements")
    assert os.path.exists(path_measurements)
    assert os.path.isfile(path_measurements.joinpath("cell_density.csv"))
    assert os.path.isfile(path_measurements.joinpath("inhibitory_fraction.csv"))

    path_illustration = path_results.joinpath("illustration")
    assert os.path.exists(path_illustration)
    assert os.path.isfile(path_illustration.joinpath("caption.txt"))
    path_cd = path_illustration.joinpath("cell_density")
    assert os.path.exists(path_cd)
    path_if = path_illustration.joinpath("inhibitory_fraction")
    assert os.path.exists(path_if)
    for region in model.subregions:
        assert os.path.isfile(path_cd.joinpath(region + ".png"))
        assert os.path.isfile(path_if.joinpath(region + ".png"))

    return True
def test_results(test_object=None):
    """
    Results section of a document.

    """
    adapter = MockAdapter()
    model = MockModel()

    if not test_object:
        document = Document("Test")
        document.methods = get_methods(document)
        results = get_results(document)
        _test_results_instance(results, adapter, model)

        value = results(adapter, model)
        _test_results_value(value, adapter, model)

        path_save = get_path_save()
        results.save(value, path_save)
        _test_results_save(path_save, adapter, model)
    else:
        try:
            results = test_object.results
        except AttributeError:
            results = test_object
        _test_results_instance(results, adapter, model)

        try:
            value = test_object.value
        except AttributeError:
            value = results(adapter, model)
        _test_results_value(value, adapter, model)

        try:
            path_save = test_object.path_save
        except AttributeError:
            path_save = get_path_save()
            path_save = results.save(path_save)
        _test_results_save(path_save, adapter, model)
    return True
