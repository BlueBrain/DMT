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
Test develop `TemplateTaggedString`
"""
from ..template import TaggedTemplateString

def test_decoding():
    """
    `TaggedTemplateString` can decode regex expressions.
    """
    key, trail =\
        TaggedTemplateString.decode(
            TaggedTemplateString.trail("__([\w]*)__"),
            "__name__!")
    assert key == "name", key
    assert trail == "!", trail

def test_tex_tags():
    """
    `TaggedTemplateString` can recognize tex-tags correctly.
    """
    s = "Cortical layers represented as \model{layer_values}."
    ts = TaggedTemplateString(s)
    assert len(ts.lines) == 1
    assert ts.lines[0] == s
    keys = ts.keys
    assert len(keys) == 1
    assert "layer_values" in keys
    layer_values = ["L1", "L2", "L3", "L4", "L6"]
    fs = ts.format(layer_values=layer_values)
    assert fs.startswith("Cortical layers represented as")
    for l in layer_values:
        assert l in fs, "{} not in {}".format(l, fs)

def test_not_available():
    """
    `TaggedTemplateString.format` should insert `Not Available` if a
    tag is not available in the namespace.
    """
    s = "Cortical layers represented as \model{layer_values}."
    ts = TaggedTemplateString(s)
    layer_values = ["L1", "L2", "L3", "L4", "L6"]
    fs = ts.format(layer_vals=layer_values)
    assert fs == "Cortical layers represented as <<<Not Available>>>."

    s = "Cortical layers represented as __layer_values__."
    ts = TaggedTemplateString(s)
    layer_values = ["L1", "L2", "L3", "L4", "L6"]
    fs = ts.format(layer_vals=layer_values)
    assert fs == "Cortical layers represented as <<<Not Available>>>."

def test_tags():
    """
    `TaggedTemplateString` can recognize __dunder__ tags correctly.
    """
    s = "Cortical layers represented as __layer_values__."
    ts = TaggedTemplateString(s)
    assert len(ts.lines) == 1
    assert ts.lines[0] == s
    keys = ts.keys
    assert len(keys) == 1
    assert "layer_values" in keys
    layer_values = ["L1", "L2", "L3", "L4", "L6"]
    fs = ts.format(layer_values=layer_values)
    assert fs.startswith("Cortical layers represented as")
    for l in layer_values:
        assert l in fs, "{} not in {}".format(l, fs)

def test_incomplete_formatting():
    """
    Incompletely formatted string should not raise, and return the string as is.
    """
    s = "Cortical layers \model{layer_value"
    ts = TaggedTemplateString(s)
    layer_values = ["L1", "L2", "L3", "L4", "L6"]
    assert ts.format(layer_values=layer_values) == s

def test_punctuation():
    """
    `TaggedTemplateString` should format punctuation in the string,
    and not remove it.
    """
    s = "Number of layers in SSCx: __number_layers__."
    ts = TaggedTemplateString(s)
    fs = ts.format(number_layers=6)
    assert fs == "Number of layers in SSCx: 6.", fs

    s = "Number of layers in SSCx: \model{number_layers}."
    ts = TaggedTemplateString(s)
    fs = ts.format(number_layers=6)
    assert fs == "Number of layers in SSCx: 6.", fs
