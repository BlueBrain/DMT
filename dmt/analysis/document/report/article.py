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
A type of document.
"""

from collections.abc import Iterable
import shutil
from pathlib import Path
from Cheetah.Template import Template
from dmt.tk.author import Author
from dmt.tk.utils.string_utils import make_label, paragraphs
from neuro_dmt.analysis.reporting import CheetahReporter
from ..import *

def _get_label(x):
    try:
        return x.label
    except AttributeError:
        return make_label(x)
    return None


class Article(Document):
    """
    A specialized type of report. 
    """
    author = Field(
        """
        Author(s) of the report.
        """,
        __default_value__=Author.anonymous)
    reporter = Field(
        """
        An object that will hold attributes generated for a model.
        """,
        __default_value__=Record)

    @field.cast(Abstract)
    def abstract(self):
        """
        Abstract of what, and how of this analysis document.
        Provide a string formatted as a latex except use double slash \\.
        Or tag with terms that can be looked up in a namespace.
        """
        return None

    def phenomenon(self):
        """
        Phenomenon studied in this lab-report.
        """
        return NA

    @field.cast(Introduction)
    def introduction(self):
        """
        Introduction to the analysis.
        Provide a string formatted as a latex except use double slash \\.
        Or tag with terms that can be looked up in a namespace.

        To include data and, an illustration in addition to a narrative,
        provide either a `Section` with these attributes, or a dictionary with
        keys `narrative`, `data`, and `illustration`.
        """
        return None

    @classmethod
    def get_class_sections(cls):
        """..."""
        return [
            cls.abstract,
            cls.introduction
        ]

    @lazyfield
    def label(self):
        """
        A single word label.
        """
        return make_label(self.title)

    def __init__(self, title, *args, **kwargs):
        """..."""
        kwargs["parent"] = self
        sections = kwargs.pop("sections", None)
        super().__init__(title, *args, **kwargs)
        self._sections = OrderedDict([
            (label, Section(title=make_title(label),
                            parent=self,
                            **content_section))
            for label, content_section in sections.items()
        ])

    def save(self, value_article, path_parent):
        """
        """
        path_article = path_parent.joinpath(self.label)
        path_article.mkdir(parents=False, exist_ok=True)

        sections = OrderedDict([
            (label, section.save(getattr(value_article, label), path_article))
            for label, section in self._sections.items()
        ])
        return Record(
            _=path_article,
            abstract=self.abstract.save(
                value_article.abstract,
                path_article),
            introduction=self.introduction.save(
                value_article.introduction,
                path_article),
            **sections)

    def __call__(self, adapter, model, *args, **kwargs):
        """
        Call me!!!
        """
        sections = OrderedDict([
            (label, section(adapter, model, *args, **kwargs))
            for label, section in self._sections.items()
        ])
        return Record(
            author=self.author,
            phenomenon=_get_label(self.phenomenon),
            label=self.label,
            abstract=self.abstract(adapter, model, *args, **kwargs),
            introduction=self.introduction(adapter, model, *args, **kwargs),
            **sections)

    def post(self, article, path_output, html=True, latex=False):
        """"..."""
        path_artefacts = self.save(article, path_output)
        if latex:
            return Record(
                latex=self.to_latex(article, path_artefacts),
                html=self.to_html(article, path_artefacts))
        return self.to_html(article, path_artefacts)

    def to_latex(self, article, path_artefacts):
        """..."""
        path_title = path_artefacts._.joinpath("title.tex")

        with open(path_title, 'w') as title_tex:
            title_tex.write("\\title{" + self.title + "}\n")
            if isinstance(self.author, Iterable):
                for i, author in enumerate(self.author):
                    title_tex.write("\\author[number]".replace("number", str(i+1))
                                    + author.affiliation + "}\n")
            else:
                title_tex.write("\\author{" + self.author.name + "}\n")
                title_tex.write("\\affil{" + self.author.affiliation + "}\n")
        path_abstract_tex = path_artefacts._.joinpath("abstract", "abstract.tex")
        with open(path_abstract_tex, 'w') as abstract_tex:
            abstract_tex.write(self.abstract.to_latex(article.abstract,
                                                      path_artefacts.abstract))

        path_introduction_tex = path_artefacts._.joinpath("introduction",
                                                          "introduction.tex")
        with open(path_introduction_tex, 'w') as introduction_tex:
            introduction_tex.write(self.introduction.to_latex(article.introduction,
                                                              path_artefacts))

                               
        latex_sections = []
        for label, section in self._sections.items():
            latex_sections += [
                "\\section*{title}\n".replace("title", make_title(label))
                ,"\\input{section/section.tex}\n".replace("section", label)
                ,"\\newpage"
            ]
            path_section_tex = path_artefacts._.joinpath(label,
                                                         "{}.tex".format(label))
            with open(path_section_tex, 'w') as section_tex:
                section_tex.write(section.to_latex(getattr(article, label),
                                                   path_artefacts))

        path_template = Path(os.path.dirname(__file__)).joinpath("article.tex")
        with open(path_template, 'r') as tex_template:
            latex = tex_template.read()


        self.logger.info(
            self.logger.get_source_info(),
            "LATEX main:", latex)
        with open(path_artefacts._.joinpath("article.tex"), 'w') as main_tex:
            main_tex.write(latex)
            for line in latex_sections:
                main_tex.write(line)
                main_tex.write("\n")
            main_tex.write("\\end{document}")

        return path_artefacts._


    def to_html(self, article, path_artefacts):
        """
        Post a article that was generated by this `Article` instance
        applied to some (adapter, model)

        Arguments
        ---------------
        article :: Results of this `Article` applied to some `(adapter, model)`
        uri :: Location where the article will be posted.
        """
        self.logger.alert(
            self.logger.get_source_info(),
            """
            Template lacking.
            First implement a HTML template,
            then the code to fill it.
            """)
        return None
