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
from .import *

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
        narrative="""
        We analyze the densities of cortical layers \model{layer_values}
        """
    )
    value_abstract = abstract(adapter, model)
    assert value_abstract.title == "Abstract", value_abstract
    assert value_abstract.label == "abstract", value_abstract
    assert value_abstract.narrative.strip().startswith(
        "We analyze the densities of cortical layers"
    ), value_abstract.narrative.strip()

    for l in adapter.get_layers(model):
        assert l in value_abstract.narrative, value_abstract

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
        narrative="""Cortical area such as the \model{brain_region} is 
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
        illustration=Record(
            figures=mock_experimental_figures,
            caption="""
            Experimentally measured cell densities used to reconstruct
            sub-regions \model{sub_brain_regions} of the
            \model{animal} \model{brain_region}.
            """))

    assert hasattr(introduction, "narrative")
    assert introduction.narrative
    assert hasattr(introduction, "illustration")
    assert introduction.illustration

    value = introduction(adapter, model)
    assert value.title == "Introduction", value.title
    assert value.label == "introduction", value.label
    assert value.illustration.caption.strip().startswith(
        "Experimentally measured"
    ), value.illustration.caption

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

def test_methods():
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

    document = Document("Test")
    methods = Methods(
        parent=document,
        narrative="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `methods` instance.
        """,
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

    assert hasattr(methods, "narrative")
    assert hasattr(methods, "measurements")
    assert isinstance(methods.measurements, MeasurementSuite)
    assert "cell_density" in methods.measurements
    assert "inhibitory_fraction" in methods.measurements

    value = methods(adapter, model)
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

    path_methods = methods.save(value, path_save)
    assert path_methods == path_save.joinpath("methods")
    assert os.path.exists(path_methods)
    assert os.path.isfile(path_methods.joinpath("narrative.txt"))
    assert os.path.isfile(path_methods.joinpath("measurements.json"))


def test_resultsI():
    """
    Results section of a document.

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

    methods = Methods(
        parent=document,
        narrative="""Random cell densities were assigned to each pair of
        (sub-region, layer) for sub-regions \\model{sub_brain_regions}
        and layers \\model{layer_values}, for the purposes of mocking the
        behavior of a `methods` instance.
        """,
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

    results = Results(
        parent=document,
        narrative="""Mock results for the purpose of test developing `Results`
        is just that --- mock. They do not really mean anything.
        """,
        data=methods.measurements,
        illustration={
            "figures": {
                "cell_density": plotter_cd,
                "inhibitory_fraction": plotter_if},
            "caption": """
            Mock figures for the purpose of test developing `Results`
            do not deserved a caption.
            """})

    assert results.title == "Results"
    assert results.label == "results"

    value_results = results(adapter, model)
    assert value_results.label == "results"
    assert value_results.title == "Results"
    assert isinstance(value_results.data, Mapping)
    assert "cell_density" in value_results.data.keys()
    assert isinstance(value_results.data["cell_density"], pd.DataFrame)
    assert "inhibitory_fraction" in value_results.data.keys()
    assert isinstance(value_results.data["inhibitory_fraction"], pd.DataFrame)
    assert value_results.narrative.startswith("Mock results for")
    assert value_results.illustration.caption.strip().startswith("Mock figures")

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
