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
import types
import inspect
import functools
from .components import *
from .report import LabReport, Article

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
        self.document = document_builder
        self.content = Record(narrative=OrderedDict(),
                              measurements=OrderedDict(),
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
            self.set_document_attribute(measurement.__name__,
                                        "measurement", unloaded)
        else:
            self.content.measurements[measurement.__name__] ={
                "description": measurement.__doc__,
                "method": measurement}
            self.set_document_attribute(measurement.__name__,
                                        "measurement", measurement)
        return measurement

    def illustration(self, illustration, set_document_attr=False):
        argspec = inspect.getfullargspec(illustration)
        caption = illustration.__doc__
        if not argspec.args and not argspec.varargs and not argspec.varkw:
            content = illustration()
            try:
                content = Path(content)
            except TypeError:
                pass
            if not callable(content) and not isinstance(content, Mapping):
                content = {illustration.__name__: content}
        else:
            content = illustration
                
        _illustration = {
            "figures": content,
            "caption": caption
        }
        self.content.illustration[illustration.__name__] = _illustration
        if set_document_attr:
            self.set_document_attribute(illustration.__name__,
                                        "illustration", content)
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
    def get_content(self, *args, **kwargs):
        content = dict(narrative=paragraphs(self.content.narrative),
                       illustration=self.content.illustration,
                       tables=self.content.tables)
        if self.content.measurements:
            content["measurements"] = self.content.measurements
        if self.content.data:
            content["data"] = self.content.data
        return content

    def get_struct(self, *args, **kwargs):
        """..."""
        return Record(
            narrative=paragraphs(self.content.narrative),
            illustration=Record(**{
                label: illustration.figures
                for label, illustration in self.content.illustration.items()}),
            tables=Record(**self.content.tables))

    def set_document_attribute(self, phenomenon, name_attribute, value_attribute):
        """
        Set an attribute on the document of which this section...
        """
        LOGGER.debug(
            LOGGER.get_source_info(),
            """
            Set attribute {}: {}
            """.format(phenomenon, name_attribute))
        try:
            phenomenon = getattr(self.document, phenomenon)
        except AttributeError:
            setattr(self.document, phenomenon, Record())
            phenomenon = getattr(self.document, phenomenon)

        setattr(phenomenon, name_attribute, value_attribute)


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
        self.document = document_builder
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
    def get_struct(self):
        return Record(
            narrative=paragraphs(self.content.narrative),
            reference_data=Record(**self.content.reference_data),
            measurements=Record(**{
                name: measurement.method
                for name, measurement in self.measurements.items()
            }))


class _ResultsBuilder(_SectionBuilder):
    """
    Build a Results section
    """
    def __init__(self, document_builder):
        super().__init__("Results", document_builder)

    # def get_content(self):
    #     """..."""
    #     return dict(
    #         narrative=paragraphs(self.content.narrative),
    #         illustration=self.content.illustration,
    #         tables=self.content.tables)

    def illustration(self, illustration):
        return super().illustration(illustration, set_document_attr=True)

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
        """..."""
        self._title = title
        self._author = author
        self.document = Document(self._title)
        self.abstract = _AbstractBuilder(self)
        self.introduction = _IntroductionBuilder(self)

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    def interfacemethod(self, function):
        """
        `function(adapter, method, *args, **kwargs)` should be added to
        this documented analysis' interface.
        """
        LOGGER.info(
            LOGGER.get_source_info(),
            """
            TO BE IMPLEMENTED:
            A function decorator to add the input function to the document's
            interface.
            """)
        return function

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

    @abstractmethod
    def get(self, *args, **kwargs):
        """..."""
        raise NotImplementedError

    @classmethod
    def chapter(cls, chapter):
        """
        chapter :: A callable...
        """
        document_builder = cls(chapter.__name__)
        document_builder.abstract = Abstract(parent=document_builder,
                                             narrative=chapter.__doc__)
        return document_builder


class LabReportBuilder(DocumentBuilder):
    """
    Build a `LabReport`.
    """
    def __init__(self, title, author=Author.anonymous):
        """
        Arguments
        ------------
        module :: Name of the module to contain the methods defined
        ~         in the document.
        """
        super().__init__(title, author)
        self.methods = _MethodsBuilder(self)
        self.results = _ResultsBuilder(self)
        self._sections = OrderedDict()

    def get(self, *args, **kwargs):
        """..."""
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

    @lazyfield
    def analysis(self):
        """..."""
        return Record(
            methods=self.methods.get_struct(),
            results=self.results.get_struct()
        )


class _SectionsCollector(Mapping):
    """
    Collect and build a document's sections.
    """
    def __init__(self, document_builder, sections=None):
        self.document = document_builder
        self._sections = OrderedDict() if not sections else sections

    def __getattr__(self, attribute):
        """..."""
        section = _SectionBuilder(attribute, self.document)
        setattr(self, attribute, section)
        self._sections[attribute] = section
        return section

    def items(self):
        return self._sections.items()

    def map_value(self, transformed):
        return self.__class__(self.document,
                              OrderedDict([
                                  (label, transformed(section))
                                  for label, section in self.items()
                              ]))

    def __getitem__(self, label):
        try:
            return self._sections[label]
        except KeyError as error:
            raise KeyError(
                "No such section: {}".format(label))
        return None

    def __iter__(self):
        return self._sections.__iter__()

    def __len__(self):
        return len(self._sections)


class ArticleBuilder(DocumentBuilder):
    """
    Build an `Article`.
    """
    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)
        self.sections = _SectionsCollector(self)


    def get(self, *args, **kwargs):
        """..."""
        return Article(
            author=self.author,
            title=self.title,
            abstract=self.abstract.get_content(),
            introduction=self.introduction.get_content(),
            sections=self.sections.map_value(lambda s: s.get_content()))
