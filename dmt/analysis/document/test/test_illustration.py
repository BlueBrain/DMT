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
Test develop `Illustration`.
"""

from dmt.tk.plotting.figure import Figure
from .import *

def test_illustration_empty():
    """
    Empty `Illustration` object should not save anything....
    """
    adapter = MockAdapter()
    model = MockModel()

    illustration = Illustration()
    value = illustration(adapter, model)
    path_save = get_path_save()
    path_test = path_save.joinpath("empty")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_save)

    path_illustration = path_test.joinpath("illustration")
    assert not os.path.exists(path_illustration)

def test_illustration_png():
    """
    An `Illustration` can be created from a PNG file sitting in the working
    directory.
    """
    adapter = MockAdapter()
    model = MockModel()

    illustration = Illustration(
        figures={"neocortical_scaffold": "resources/neocortical_scaffold.png"},
        caption="""
        The neocortex is a 2-3 mm thick sheet of tissue on the surface of the brain. The figure above shows a digitally reconstructed neocortical column.
        """)
    assert illustration.figures
    assert "neocortical_scaffold" in illustration.figures
    value = illustration(adapter, model)

    assert isinstance(value.figures, Mapping)
    assert "neocortical_scaffold" in value.figures
    assert isinstance(value.figures["neocortical_scaffold"], Figure)
    assert value.caption.strip().startswith(
        "The neocortex is a 2-")

    path_save = get_path_save()
    path_test = path_save.joinpath("illustration_png")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    assert os.path.exists(
        path_illustration)
    assert os.path.isfile(
        path_illustration.joinpath("neocortical_scaffold.png"))
    assert os.path.isfile(
        path_illustration.joinpath("caption.txt"))


def test_illustration_single_graphic_figure():
    """
    An `Illustration` can be created from a figure object (not a callable).
    """
    adapter = MockAdapter()
    model = MockModel()

    caption = "Mock cell density for \model{layer_type} layers."

    plotter = Bars(xvar="layer", xlabel="Layer",
                   yvar="cell_density", ylabel="Cell Density")
    mock_bars = plotter(mock_cell_density())
    illustration = Illustration(
        figures=mock_bars,
        caption=caption)
    assert illustration.figures
    value = illustration(adapter, model)

    assert isinstance(value.figures, Mapping)
    assert value.caption == "Mock cell density for cortical layers.",\
        value.caption

    path_save = get_path_save()
    path_test = path_save.joinpath("illustration_single_graphic_figure")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    assert os.path.exists(
        path_illustration)
    assert os.path.isfile(
        path_illustration.joinpath("cell_density.png"))
    assert os.path.isfile(
        path_illustration.joinpath("caption.txt"))

def test_illustration_single_graphic_callable_figure():
    """
    An `Illustration` can be created from a figure object.
    """
    adapter = MockAdapter()
    model = MockModel()

    caption = "Mock cell density for \model{layer_type} layers."
    bars = Bars(xvar="layer", xlabel="Layer",
                yvar="cell_density", ylabel="Cell Density")
    illustration =\
        Illustration(figures=bars, caption=caption)
    assert illustration.figures
    value =\
        illustration(adapter, model, data=mock_cell_density)

    assert isinstance(value.figures, Mapping)
    assert value.caption == "Mock cell density for cortical layers.",\
        value.caption

    path_save = get_path_save()
    path_test = path_save.joinpath(
        "illustration_single_graphic_callable_figure")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    assert os.path.isfile(
        path_illustration.joinpath("cell_density.png"))
    assert os.path.isfile(
        path_illustration.joinpath("caption.txt"))

def test_illustration_multi_graphic_figure():
    """
    An `Illustration` can be created from a Mapping label->figure object.
    """
    adapter = MockAdapter()
    model = MockModel()

    caption = "Mock composition for \model{layer_type} layers."

    plotter_cd = Bars(xvar="layer", xlabel="Layer",
                      yvar="cell_density", ylabel="Cell Density")
    figures = plotter_cd(mock_cell_density())
    plotter_if = Bars(xvar="layer", xlabel="Layer",
                      yvar="inhibitory_fraction", ylabel="Inhibitory Fraction")
    figures.update(plotter_if(mock_inh_fraction()))

    illustration = Illustration(figures=figures, caption=caption)

    assert illustration.figures
    value = illustration(adapter, model)

    assert isinstance(value.figures, Mapping)
    assert value.caption == "Mock composition for cortical layers.",\
        value.caption

    path_save = get_path_save()
    path_test = path_save.joinpath(
        "illustration_multi_graphic_figure")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    assert os.path.isfile(
        path_illustration.joinpath("caption.txt"))
    assert os.path.isfile(
        path_illustration.joinpath("cell_density.png"))
    assert os.path.isfile(
        path_illustration.joinpath("inhibitory_fraction.png"))

def test_illustration_multi_nested_graphic_figure():
    """
    An `Illustration` can be created from a
    Mapping{label-> Mapping{sublabel->figure object}}

    The outer mapping can be used for different phenomena,
    and the inner mapping for a group of figures for a given phenomenon.
    """
    adapter = MockAdapter()
    model = MockModel()

    caption = "Mock composition for \model{layer_type} layers."

    data_cd = pd.concat([
        mock_cell_density().assign(region=region)
        for region in model.subregions])
    data_if = pd.concat([
        mock_inh_fraction().assign(region=region)
        for region in model.subregions])

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

    figures ={
        "cell_density": plotter_cd(data_cd),
        "inhibitory_fraction": plotter_if(data_if)}
    illustration = Illustration(figures=figures, caption=caption)

    assert illustration.figures
    value = illustration(adapter, model)

    assert isinstance(value.figures, Mapping)
    assert value.caption == "Mock composition for cortical layers.",\
        value.caption

    path_save = get_path_save()
    path_test = path_save.joinpath(
        "illustration_multi_nested_graphic_figure")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    path_cd = path_illustration.joinpath("cell_density")
    path_if = path_illustration.joinpath("inhibitory_fraction")

    assert os.path.isfile(path_illustration.joinpath("caption.txt"))
    assert os.path.exists(path_cd)
    assert os.path.exists(path_if)
    for region in model.subregions:
        assert os.path.isfile(path_cd.joinpath(region + ".png"))
        assert os.path.isfile(path_if.joinpath(region+".png"))

def test_illustration_multi_nested_graphic_callable_figure():
    """
    An `Illustration` can be created from a
    Mapping{label-> Mapping{sublabel->figure callable}}

    The outer mapping can be used for different phenomena,
    and the inner mapping for a group of figures for a given phenomenon.
    """
    adapter = MockAdapter()
    model = MockModel()

    caption = "Mock composition for \\model{layer_type} layers."

    data_cd = pd.concat([
        mock_cell_density().assign(region=region)
        for region in model.subregions])
    data_if = pd.concat([
        mock_inh_fraction().assign(region=region)
        for region in model.subregions])
    data ={
        "cell_density": data_cd,
        "inhibitory_fraction": data_if}

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
    figures ={
        "cell_density": plotter_cd,
        "inhibitory_fraction": plotter_if}

    illustration = Illustration(figures=figures, caption=caption)

    assert illustration.figures
    value =\
        illustration(adapter, model, data=data)

    assert isinstance(value.figures, Mapping)
    assert value.caption == "Mock composition for cortical layers.",\
        value.caption

    path_save = get_path_save()
    path_test = path_save.joinpath(
        "illustration_multi_nested_graphic_callable_figure")
    path_test.mkdir(parents=False, exist_ok=True)
    illustration.save(value, path_test)

    path_illustration = path_test.joinpath("illustration")
    path_cd = path_illustration.joinpath("cell_density")
    path_if = path_illustration.joinpath("inhibitory_fraction")

    assert os.path.isfile(path_illustration.joinpath("caption.txt"))
    assert os.path.exists(path_cd)
    assert os.path.exists(path_if)
    for region in model.subregions:
        assert os.path.isfile(path_cd.joinpath(region + ".png"))
        assert os.path.isfile(path_if.joinpath(region+".png"))

    return True
