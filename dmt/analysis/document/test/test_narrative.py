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
Test develop `Narrative`.
"""
from .import *

def test_narrative():
    """
    A `Narrative` should:
    1. return a string
    2. insert keywords in the template.
    """
    adapter = MockAdapter()
    model = MockModel()
    s = "We analyze the densities of cortical layers"
    narrative = Narrative(text=s+" \model{layer_values}.")

    story = narrative(adapter, model)
    assert isinstance(story, str), story
    assert story.startswith(s), story
    for l in adapter.get_layers(model):
        assert l in story, story

    path_save = get_path_save()
    narrative.save(story, path_save)

    assert os.path.isfile(path_save.joinpath("narrative.txt"))


