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
Test develop document components.
"""
from .. import *


class MockModel:
    pass


class MockAdapter:
    """..."""
    def get_label(self, model):
        return "MockModel"

    def get_provenance(self, model, **kwargs):
        return dict(
            animal="mock",
            age="mock",
            brain_region="mock",
            data_release="mock",
            label="mock",
            uri="mock",
            authors=["mock"])


def test_narrative():
    """
    Narrative should:
    1. return a string
    2. insert keywords in the template.
    """
    adapter = MockAdapter()
    model = MockModel()
    narrative = Narrative("Test narrative $animal model $label")

    provenance = adapter.get_provenance(model)

    story_mock = narrative(adapter, model)
    assert isinstance(story_mock, str)
    words = story_mock.split(' ')
    assert words[2] == "mock", words[2]
    assert words[4] == "mock", words[2]

    provenance = dict(animal="unknown", label="unknown")
    story_unknown = narrative(adapter, model, provenance=provenance)
    assert isinstance(story_unknown, str)
    words = story_unknown.split(' ')
    assert words[2] == "unknown", words[2]
    assert words[4] == "unknown", words[2]

    return story_mock, story_unknown


