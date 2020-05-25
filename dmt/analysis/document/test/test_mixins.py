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
Test develop document components by mixing...
"""
from .import *

class Abstract(DocElem, Narrative):
    """
    Abstract is a component of a document.
    """
    title = "Abstract"
    label = "abstract"


class Introduction(DocElem, Narrative, Illustration):
    """
    The introduction to a document.
    """
    title = "Introduction"
    label = "introduction"


class Methods(DocElem, Narrative, Data, Illustration):
    """
    The methods section of a document.
    """
    title = "Methods"
    label = "methods"


class Results(DocElem, Narrative, Data, Illustration):
    """
    The results of a document.
    """
    title = "Results"
    label = "results"


def test_abstract():
    """
    An `Abstract` should:
    1. have a title
    2. have a label
    3. have a narrative
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")
    abstract = Abstract(
        parent=document,
        text="We analyze the densities of cortical layers \model{layer_values}"
    )
    value_abstract = abstract(adapter, model)
    assert value_abstract.title == "Abstract", value_abstract
    assert value_abstract.label == "abstract", value_abstract
    assert value_abstract.narrative.startswith(
        "We analyze the densities of cortical layers"
    ), value_abstract
    for l in adapter.get_layers(model):
        assert l in value_abstract.narrative, value_abstract

    path_save = get_path_save()
    abstract.save(value_abstract, path_save)

    path_abstract = path_save.joinpath("abstract")
    assert os.path.isfile(path_abstract.joinpath("narrative.txt"))

def test_introduction():
    """
    An `Introduction`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. may have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")

    mock_experimental_figures = Bars(
        xvar="layer", xlabel="Layer",
        yvar="cell_density", ylabel="Cell Density"
    )(mock_cell_density())
    mock_experimental_figures.update(Bars(
        xvar="layer", xlabel="Layer",
        yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"
    )(mock_inh_fraction()))

    introduction = Introduction(
        parent=document,
        text="""Cortical area such as the \model{brain_region} is 
        composed of layers of cells with different cell densities.
        In this report we analyze circuit composition of cortical layers
        \model{layer_values}, focusing on total cell density and the fraction 
        of inhibitory neurons in each layer.
        In our model of the \model{brain_region} we have reconstructed
        the sub-regions \model{sub_brain_regions}.
        Experimental measurements for cell densities for these sub-regions
        were not available. Hence we have used the same cell densities 
        presented in the figure for each of the these regions.
        """,
        figures=mock_experimental_figures,
        caption="""Experimentally measured cell densities used to reconstruct
        sub-regions \model{sub_brain_regions} of the
        \model{animal} \model{brain_region}.
        """)

    value = introduction(adapter, model)
    assert value.title == "Introduction", value.title
    assert value.label == "introduction", value.label
    assert value.illustration.caption.startswith("Experimentally measured")

    path_save = get_path_save()
    introduction.save(value, path_save)

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

def get_methods():
    """
    Create a `Methods` instance to test.
    """
    document = Document("Test")
    return Methods(
        parent=document,
        text="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `Methods` instance.
        """,
        measurement={
            "cell_density": Data.Collector(
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=cell_density,
                sample_size=20),
            "inhibitory_fraction": Data.Collector(
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=inhibitory_fraction,
                sample_size=20)})

def test_methods():
    """
    A `Methdos`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. should be able to measure (adapter, model)
    5. may have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()

    methods = get_methods()

    value_methods = methods(adapter, model)

    try:
        value_methods.illustration
        assert False
    except AttributeError:
        pass

    assert isinstance(value_methods.data, Mapping), type(value_methods.data)

    #TODO: test that the methods value is as expected

    path_save = get_path_save()
    methods.save(value_methods, path_save)

    path_methods = path_save.joinpath("methods")

    assert os.path.exists(path_methods)
    path_data = path_methods.joinpath("data")
    assert os.path.exists(path_data)
    assert os.path.isfile(path_data.joinpath("cell_density.csv"))
    assert os.path.isfile(path_data.joinpath("inhibitory_fraction.csv"))

    path_illustration = path_methods.joinpath("illustration")
    assert not os.path.exists(path_illustration)

    #TODO: Test that the saved data are as expected

    return True

def test_methods_no_data():
    """
    A `Methods` without data should not create a folder/file `data`...
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")

    methods = Methods(
        parent=document,
        text="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `Methods` instance.
        """)

    value_methods = methods(adapter, model)

    assert value_methods.narrative
    try:
        value_methods.data
        assert False
    except AttributeError:
        pass
    try:
        value_methods.illustration
        assert False
    except AttributeError:
        pass

    #TODO: test that the methods value is as expected

    path_save = get_path_save()
    path_this = path_save.joinpath("no_data")
    path_this.mkdir(parents=False, exist_ok=True)
    methods.save(value_methods, path_this)

    path_methods = path_this.joinpath("methods")

    assert os.path.exists(path_methods)
    path_data = path_methods.joinpath("data")
    assert not os.path.exists(path_data)

    path_illustration = path_methods.joinpath("illustration")
    assert not os.path.exists(path_illustration)

    return True

def test_results():
    """
    A `Results`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. should provide a statistical summary
    5. should have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")
    caption = "Mock composition for \model{layer_type} layers."

    plotter_cd = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density"))
    plotter_if = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"))

    results = Results(
        parent=document,
        text="""Mock results for the purpose of test developing `Results`
        is just that --- mock. They do not really mean anything.
        """,
        measurement={
            "cell_density": Data.Collector(
                label="cell_density",
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=cell_density,
                sample_size=20),
            "inhibitory_fraction": Data.Collector(
                label="inhibitory_fraction",
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=inhibitory_fraction,
                sample_size=20)},
        figures={
            "cell_density": plotter_cd,
            "inhibitory_fraction": plotter_if},
        caption="""Mock figures for the purpose of test developing `Results`
        do not deserved a caption.
        """)

    value_results = results(adapter, model)

    assert value_results.label == "results"
    assert value_results.title == "Results"
    assert isinstance(value_results.data, Mapping)
    assert "cell_density" in value_results.data.keys()
    assert isinstance(value_results.data["cell_density"], pd.DataFrame)
    assert "inhibitory_fraction" in value_results.data.keys()
    assert isinstance(value_results.data["inhibitory_fraction"], pd.DataFrame)
    assert value_results.narrative.startswith("Mock results for")
    assert value_results.illustration.caption.startswith("Mock figures")

    path_save = get_path_save()
    results.save(value_results, path_save)

    path_results = path_save.joinpath("results")
    assert os.path.exists(path_results)
    assert os.path.isfile(path_results.joinpath("narrative.txt"))

    path_data = path_results.joinpath("data")
    assert os.path.isfile(path_data.joinpath("cell_density.csv"))
    assert os.path.isfile(path_data.joinpath("inhibitory_fraction.csv"))

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

def test_results_no_data():
    """
    A `Results`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. should provide a statistical summary
    5. should have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")
    caption = "Mock composition for \model{layer_type} layers."

    plotter_cd = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density"))
    plotter_if = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"))
    value_cell_density = Data.Collector(
        label="cell_density",
        parameters=Parameters(
            regions_and_layers,
            labels=("region", "layer")),
        method=cell_density,
        sample_size=20)(adapter, model)
    value_inhibitory_fraction = Data.Collector(
        label="inhibitory_fraction",
        parameters=Parameters(
            regions_and_layers,
            labels=("region", "layer")),
        method=inhibitory_fraction,
        sample_size=20)(adapter, model)
    results = Results(
        parent=document,
        text="""Mock results for the purpose of test developing `Results`
        is just that --- mock. They do not really mean anything.
        """,
        figures={
            "cell_density": plotter_cd(value_cell_density),
            "inhibitory_fraction": plotter_if(value_inhibitory_fraction)},
        caption="""Mock figures for the purpose of test developing `Results`
        do not deserved a caption.
        """)
    
    value_results = results(adapter, model)

    assert value_results.label == "results"
    assert value_results.title == "Results"
    try:
        value_results.data
        assert False
    except AttributeError:
        pass
    assert value_results.narrative.startswith("Mock results for")
    assert value_results.illustration.caption.startswith("Mock figures")

    path_save = get_path_save()
    path_test = path_save.joinpath("no_data")
    path_test.mkdir(parents=False, exist_ok=True)
    results.save(value_results, path_test)

    path_results = path_test.joinpath("results")
    assert os.path.exists(path_results)
    assert os.path.isfile(path_results.joinpath("narrative.txt"))

    path_data = path_results.joinpath("data")
    assert not os.path.exists(path_data)

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

def test_results_no_illusrtration():
    """
    A `Results`
    1. should have a title
    2. should have a label
    3. should have a story to tell
    4. should provide a statistical summary
    5. should have an illustration to show
    """
    adapter = MockAdapter()
    model = MockModel()
    document = Document("Test")
    caption = "Mock composition for \model{layer_type} layers."

    plotter_cd = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="cell_density", ylabel="Cell Density"))
    plotter_if = MultiPlot(
        mvar="region",
        plotter=Bars(
            xvar="layer", xlabel="Layer",
            yvar="inhibitory_fraction", ylabel="Inhibitory Fraction"))

    results = Results(
        parent=document,
        text="""Mock results for the purpose of test developing `Results`
        is just that --- mock. They do not really mean anything.
        """,
        measurement={
            "cell_density": Data.Collector(
                label="cell_density",
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=cell_density,
                sample_size=20),
            "inhibitory_fraction": Data.Collector(
                label="inhibitory_fraction",
                parameters=Parameters(
                    regions_and_layers,
                    labels=("region", "layer")),
                method=inhibitory_fraction,
                sample_size=20)})

    value_results = results(adapter, model)

    assert value_results.label == "results"
    assert value_results.title == "Results"
    assert isinstance(value_results.data, Mapping)
    assert "cell_density" in value_results.data.keys()
    assert isinstance(value_results.data["cell_density"], pd.DataFrame)
    assert "inhibitory_fraction" in value_results.data.keys()
    assert isinstance(value_results.data["inhibitory_fraction"], pd.DataFrame)
    assert value_results.narrative.startswith("Mock results for")
    try:
        value_results.illustration
        assert False
    except AttributeError:
        pass

    path_save = get_path_save()
    path_test = path_save.joinpath("no_illustration")
    path_test.mkdir(parents=False, exist_ok=True)
    results.save(value_results, path_test)

    path_results = path_test.joinpath("results")
    assert os.path.exists(path_results)
    assert os.path.isfile(path_results.joinpath("narrative.txt"))

    path_data = path_results.joinpath("data")
    assert os.path.isfile(path_data.joinpath("cell_density.csv"))
    assert os.path.isfile(path_data.joinpath("inhibitory_fraction.csv"))

    path_illustration = path_results.joinpath("illustration")
    assert not os.path.exists(path_illustration)

    return True

