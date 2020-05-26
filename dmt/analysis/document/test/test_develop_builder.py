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
from collections import OrderedDict
from dmt.tk.field import NA, Record
from dmt.tk.journal import Logger
from ..components import *
from .import *

"""
TODO: The author of a document should enter the content as methods.
What should the arguments of these methods be?
"""
LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def paragraphs(narrative):
    """
    Lines of a narrative

    Arguments
    -------------
    narrative :: Mapping
    """
    def _paragraph(label, content):
        if label == "_":
            return "\t" + content
        return "{}:\t{}".format(label, content)
    return "\n\n".join(
        _paragraph(label, content)
        for label, content in narrative.items())


class _AbstractBuilder:
    def __init__(self, document_builder):
        self.document_builder = document_builder
        self.content = OrderedDict()

    def __call__(self, narrative):
        """
        TODO: Argument `narrative` should be a callable.
        """
        LOGGER.devnote(
            LOGGER.get_source_info(),
            """
            Add content {} to abstract:
            {}
            """.format(narrative.__name__, narrative.__doc__))
        self.content[narrative.__name__] = narrative.__doc__
        return narrative

    def get(self):
        """..."""
        return Abstract(
            parent=self.document_builder.document,
            narrative=paragraphs(self.content))

class _IntroductionBuilder:
    def __init__(self, document_builder):
        self._document_builder = document_builder
        self._content = Record(narrative=OrderedDict(),
                               illustration=OrderedDict())

    def illustration(self, illustration):
        self._content.illustration[illustration.__name__] = {
            "figures": illustration,
            "caption": illustration.__doc__
        }

    def __call__(self, narrative):
        self._content.narrative[narrative.__name__] = narrative

class DocumentBuilder:
    """
    A context manager to help build a document.
    """
    def __init__(self, title):
        self._title = title
        self.document = Document(self._title)
        self.abstract = _AbstractBuilder(self)

    @property
    def title(self):
        return self._title

    def __enter__(self):
        """
        Start building the document.
        """
        return self

    def __exit__(self, type_exception, value_exception, traceback):
        if type_exception:
            raise value_exception
        return True


def test_context_management():
    """Test context management functionality of `DocumentBuilder`"""

    adapter = MockAdapter()
    model = MockModel()

    with DocumentBuilder("Test") as document:
        assert document.title == "Test"

        assert isinstance(document.abstract, _AbstractBuilder)
        assert document.abstract.document_builder == document

        @document.abstract
        def _():
            """
            We use Python context managers to write programmed documents.
            In literate programming, code is embedded into written language.
            With Python, we can leverage doc-strings to embed written language
            part of a document into Python code.
            An narrative can be should be added as the doc-string.
            In this case this doc-string will appear in the abstract.
            """
            pass

        assert document.abstract.content
        assert '_' in document.abstract.content
        abstract = document.abstract.get()
        assert isinstance(abstract, Abstract)
        value_abstract = abstract(adapter, model)
        LOGGER.alert(
            LOGGER.get_source_info(),
            """
            Abstract builder's narrative:
            {}
            """.format(value_abstract.narrative))
        assert value_abstract.narrative.strip().startswith("We use Python")



