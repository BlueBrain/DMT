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
Test that document components are castable...
"""
from frozendict import frozendict
from .import *


def test_narrative():
    """
    A `Narrative` can be cast from a string.
    """
    class _Section(DocElem):
        """Test Section"""
        def __init__(self, title, *args, **kwargs):
            super().__init__(*args, title=title, **kwargs)

        @field.cast(Narrative)
        def narrative(self):
            return "Test"

        def __call__(self, adapter, model):
            return Record(narrative=self.narrative(adapter, model))


    d = Document("test")
    s = _Section("Abstract", parent=d)
    assert isinstance(s.narrative, Narrative), type(s.narrative)

    v = s(MockAdapter(), MockModel())
    assert v.narrative == "Test"

def test_data():
    """
    A `Data` can be cast from a `pandas.DataFrame`.
    """
    class _Section(DocElem):
        """Test Section"""
        def __init__(self, title, *args, **kwargs):
            super().__init__(*args, title=title, **kwargs)

        @field.cast(Data)
        def data(self):
            return mock_cell_density()

        def __call__(self, adapter, model):
            return Record(data=self.data(adapter, model))


    d = Document("test")
    s = _Section("Data", parent=d)
    assert isinstance(s.data, Data), type(s.data)

    v = s(MockAdapter(), MockModel())
    assert isinstance(v.data, pd.DataFrame)
    assert "layer" in v.data.columns
    assert "cell_density" in v.data.columns

def test_narrative_data():
    """
    A `Narrative` can be cast from a text,
    and ` Data` can be cast from a `pandas.DataFrame`
    """
    class _Section(DocElem):
        """Test Section"""
        def __init__(self, title, *args, **kwargs):
            super().__init__(*args, title=title, **kwargs)

        @field.cast(Narrative)
        def narrative(self):
            return "Test"

        @field.cast(Data)
        def data(self):
            return mock_cell_density()

        def __call__(self, adapter, model):
            return Record(
                narrative=self.narrative(adapter, model),
                data=self.data(adapter, model))

    d = Document("test")
    s = _Section("Data", parent=d)
    assert isinstance(s.narrative, Narrative), type(s.narrative)
    assert isinstance(s.data, Data), type(s.data)

    v = s(MockAdapter(), MockModel())
    assert v.narrative == "Test"
    assert isinstance(v.data, pd.DataFrame)
    assert "layer" in v.data.columns
    assert "cell_density" in v.data.columns


def test_illustration():
    """
    A `Illustration` can be cast from a dict.
    """
    class _Section(DocElem):
        """Test Section"""
        def __init__(self, title, *args, **kwargs):
            super().__init__(*args, title=title, **kwargs)

        @field.cast(Narrative)
        def narrative(self):
            raise FieldIsRequired

        @field.cast(Data)
        def data(self):
            return NA

        @field.cast(Illustration)
        def illustration(self):
            return NA

        def __call__(self, adapter, model):
            return Record(
                narrative=self.narrative(adapter, model),
                data=self.data(adapter, model),
                illustration=self.illustration(adapter, model))


    p = Bars(xvar="layer", xlabel="Layer",
             yvar="cell_density", ylabel="Cell Density")
    d = Document("test")
    s = _Section("Illustration", parent=d,
                 narrative="Test",
                 data=mock_cell_density(),
                 illustration=frozendict(
                     caption="Caption",
                     figures=p(mock_cell_density())))
    assert isinstance(s.narrative, Narrative), type(s.narrative)
    assert isinstance(s.data, Data), type(s.data)
    try:
        illustration = s.illustration
    except AttributeError:
        assert False

    assert isinstance(illustration, Illustration), type(illustration)

    v = s(MockAdapter(), MockModel())
    
    assert v.narrative == "Test"
    assert isinstance(v.data, pd.DataFrame)
    assert "layer" in v.data.columns
    assert "cell_density" in v.data.columns
    try:
        vill = v.illustration
    except AttributeError:
        assert False

    try:
        caption = vill.caption
    except AttributeError:
        assert False
    assert caption == "Caption"
    
    try:
        figures = vill.figures
    except AttributeError:
        assert False


def test_narrative_data_illustration():
    """
    A `Narrative`, `Data`, and `Illustration` can all be cast from a dict.
    """
    class _Section(DocElem):
        """Test Section"""
        def __init__(self, title, *args, **kwargs):
            super().__init__(*args, title=title, **kwargs)

        @field.cast(Illustration)
        def illustration(self):
            return NA
        def __call__(self, adapter, model):
            return Record(
                illustration=self.illustration(adapter, model))


    p = Bars(xvar="layer", xlabel="Layer",
             yvar="cell_density", ylabel="Cell Density")
    d = Document("test")
    s = _Section("Illustration", parent=d,
                 illustration=frozendict(
                     caption="Caption",
                     figures=p(mock_cell_density())))
    try:
        illustration = s.illustration
    except AttributeError:
        assert False

    assert isinstance(illustration, Illustration), type(illustration)

    v = s(MockAdapter(), MockModel())
    
    try:
        vill = v.illustration
    except AttributeError:
        assert False

    try:
        caption = vill.caption
    except AttributeError:
        assert False
    assert caption == "Caption"
    
    try:
        figures = vill.figures
    except AttributeError:
        assert False
