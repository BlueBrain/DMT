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
Build a document
"""
import inspect
import functools
from .components import *
from .report import LabReport

LOGGER = Logger(client=__file__, level=Logger.Level.STUDY)

def paragraphs(narrative):
    """
    Lines of a narrative

    Arguments
    -------------
    narrative :: Mapping

    TODO:
    This a hotfix assuming latex processing.
    Refactor code to allow the latex requirement implemented as this hotfix.
    """
    def _paragraph(label, content):
        if label == "_":
            return '\t' + content  + "\n\n"
        p = "\n\n{\\bf title}:\t".replace("title",
                                   ' '.join(w.capitalize()
                                            for w in label.split('_')))
        p += content
        return p + "\\\\\n\n"

    return '\n'.join(
        _paragraph(label, content)
        for label, content in narrative.items())


class _SectionBuilder:
    """
    Build a document's section.
    """
    def __init__(self, title, document_builder):
        self.title = title
        self.document_builder = document_builder
        self.content = Record(
            narrative=OrderedDict(),
            data=OrderedDict(),
            tables=CompositeData(),
            illustration=OrderedDict())

    def data(self, data):
        """
        TODO: Rethink `Section.data` to behave like illustration.
        TODO: Distinguish between `Data` and `Measurement`.
        ~     `Measurement` should be based on `Data`,
        ~     the difference that `Measurement` should be a
        ~     `Callable(adapter -> model -> Data)`.
        ~     Resulting `Data` should have the same description as the
        ~     `Measurement`, with additional
        ~     information about the adapter and model.
        ~     In accordance, there should be `CompositeMeasurement` and
        ~     `CompositeData`.
        """
        raise NotImplementedError

    def illustration(self, illustration):
        argspec = inspect.getfullargspec(illustration)
        if not argspec.args and not argspec.varargs and not argspec.varkw:
            caption = illustration.__doc__
            content = illustration()
            try:
                content = Path(content)
            except TypeError:
                pass
            if not callable(content) and not isinstance(content, Mapping):
                content = {illustration.__name__: content}

        self.content.illustration[illustration.__name__] = {
            "figures": content,
            "caption": caption
        }
        return illustration


    def tables(self, table):
        """
        TODO: Add description to `CompositeData` that can be picked up
        ~     from a doc-string...
        """
        argspec = inspect.getfullargspec(table)
        if not argspec.args and not argspec.varargs and not argspec.varkw:
            value = table()
        else:
            value = table

        self.content.tables.assign(**{
            table.__name__: value
        })
        return table

    def __call__(self, narrative):
        self.content.narrative[narrative.__name__] = narrative.__doc__
        return narrative

    def with_parent(self, document):
        """
        TODO: What about Section data? Think about it.
        """
        return Section(
            parent=document,
            title=self.title,
            narrative=paragraphs(self.content.narrative),
            illustration=self.content.illustration,
            tables=self.content.tables)
    def get_content(self):
        return dict(
            narrative=paragraphs(self.content.narrative),
            illustration=self.content.illustration,
            tables=self.content.tables)


class _AbstractBuilder:
    def __init__(self, document_builder):
        self.document_builder = document_builder
        self.content = OrderedDict()

    def __call__(self, narrative):
        """
        TODO: Argument `narrative` should be a callable.
        """
        self.content[narrative.__name__] = narrative.__doc__
        return narrative

    def with_parent(self, document):
        """..."""
        return Abstract(
            parent=self.document_builder.document,
            narrative=paragraphs(self.content))
    def get_content(self):
        return dict(
            narrative=paragraphs(self.content))


class _IntroductionBuilder(_SectionBuilder):

    def __init__(self, document_builder):
        super().__init__("Introduction", document_builder)

    def with_parent(self, document):
        """..."""
        return Introduction(
            parent=document,
            narrative=paragraphs(self.content.narrative),
            tables=self.content.tables,
            illustration=self.content.illustration)
    def get_content(self):
        return dict(
            narrative=paragraphs(self.content.narrative),
            tables=self.content.tables,
            illustration=self.content.illustration)
    

class _MethodsBuilder(_SectionBuilder):
    """
    Build `Methods`
    """
    def __init__(self, document_builder):
        """..."""
        self.title = "Methods"
        self.document_builder = document_builder
        self.content = Record(narrative=OrderedDict(),
                               data=OrderedDict(),
                               reference_data=CompositeData(),
                               measurements=OrderedDict(),
                               illustration=OrderedDict())

    def reference_data(self, reference_data):
        """
        TODO: Add description to `CompositeData` that can be picked up
        ~     from a doc-string...
        """
        argspec = inspect.getfullargspec(reference_data)
        if not argspec.args and not argspec.varargs and not argspec.varkw:
            value = reference_data()
        else:
            try:
                value = reference_data()
            except TypeError:
                raise NotImplementedError(
                    """
                    Implementation will require us to decide when `reference_data`
                    will be evaluated. The arguments could be passed through
                    keyword arguments.
                    """)
        
        self.content.reference_data.assign(**{
            reference_data.__name__: value
        })
        return reference_data

    def measurements(self, measurement):
        """
        One measurement at a time.
        """
        argspec = inspect.getfullargspec(measurement)
        if not argspec.args and not argspec.varargs and not argspec.varkw:
            unloaded = measurement()
            if isinstance(unloaded, (Measurement, Mapping)):
                self.content.measurements[measurement.__name__] =\
                    unloaded
            elif callable(unloaded):
                self.content.measurements[measurement.__name__] ={
                    "description": measurement.__doc__,
                    "method": unloaded}
            else:
                raise TypeError(
                    """
                    Measurement of a model must be a callable.
                    """)
        else:
            self.content.measurements[measurement.__name__] ={
                "description": measurement.__doc__,
                "method": measurement}
        return measurement

    def with_parent(self, document):
        return Methods(
            parent=document,
            narrative=paragraphs(self.content.narrative),
            reference_data=CompositeData(self.content.reference_data),
            measurements=self.content.measurements)
    def get_content(self):
        return {
            "narrative": paragraphs(self.content.narrative),
            "reference_data": self.content.reference_data,
            "measurements": self.content.measurements}


class _ResultsBuilder(_SectionBuilder):
    """
    Build a Results section
    """
    def __init__(self, document_builder):
        super().__init__("Results", document_builder)

    def get_content(self):
        """..."""
        return dict(
            narrative=paragraphs(self.content.narrative),
            illustration=self.content.illustration,
            tables=self.content.tables)

    def with_parent(self, document):
        """..."""
        return Results(
            parent=document,
            narrative=paragraphs(self.content.narrative),
            illustration=self.content.illustration,
            tables=self.content.tables)


class DocumentBuilder:
    """
    A context manager to help build a document.
    """
    def __init__(self, title, author=Author.anonymous):
        self._title = title
        self._author = author
        self.document = Document(self._title)
        self.abstract = _AbstractBuilder(self)
        self.introduction = _IntroductionBuilder(self)
        self.methods = _MethodsBuilder(self)
        self.results = _ResultsBuilder(self)
        self._sections = OrderedDict()

    @property
    def author(self):
        return self._author

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

    def section(self, title):
        if title not in self._sections:
            self._sections[title] =\
                _SectionBuilder(title=title, document_builder=self)
        return self._sections[title]

    def get(self, *args, **kwargs):
        return LabReport(
            author=self.author,
            title=self.title,
            abstract=self.abstract.get_content(),
            introduction=self.introduction.get_content(),
            methods=self.methods.get_content(),
            results=self.results.get_content(),
            sections=OrderedDict([
                (title, section.get_content())
                for title, section in self._sections.items()]))

    def chapter(self, chapter):
        """
        chapter :: A callable...
        """
        document_builder = DocumentBuilder(
            chapter.__name__
        )
        document_builder.abstract = Abstract(
            parent=document_builder,
            narrative=chapter.__doc__
        )
        return document_builder
