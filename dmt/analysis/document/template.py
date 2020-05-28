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
Templated string that can be filled in with a namespace.
** ~TemplateTaggedString~
   We are greedy, we want everything.
   A string representing, for example, the abstract, may contain tags to be
   filled by method calls on ~(adapter, model, *args, **kwargs)~.
   How can we then distinguish any other word from a template tag?
   We could use ` ~$~, but we want to allow latex!
   Allowing latex also overrules using native python string templates that use
   ~{template-tag}~ syntax.
   We have to think of a /latexical/ way.
   Possibilities:
   1. ~\tag{word}~ too latexy? plus the word ~tag~ may clash...
   2. ~\dmtag{word}~_ too latexy? ~am~? really?
   3. ~<<word>>~ (problem with latex, though rarer than ~{word}~
   4. ~__word__~ sorta-pythonic. user does not have to know latex
   5. ~\query{word}~ meh
   6. ~\ttag{word}~ whatever
   7. a mix of latex sorta approach, and pythonic dunders.
"""

from collections import OrderedDict
import re
from Cheetah.Template import Template
from pathlib import Path
from dmt.model import AIBase
from dmt.model.interface import interfacemethod
from dmt.data.observation.measurement import\
    collection as measurement_collection
from dmt.tk.journal import Logger
from dmt.tk.parameters import Parameters
from dmt.tk.field import\
    field, Field,\
    lambdafield, LambdaField,\
    lazyfield,\
    NA, Record,\
    WithFields
from dmt.tk.utils.string_utils import make_label
from neuro_dmt import terminology


class TaggedTemplateString(WithFields):
    """
    Defines a string to be 
    """
    cmds_latex = Field(
        """
        Latex command word.
        """,
        __default_value__={"\model"})
    tags = Field(
        """
        Regular expressions that a word in a text should match...
        the default value considers anything surrounded by dunders is
        a tag. This relies on a pre-filtering of words.
        We are too lazy to find a better regex at this point of development.
        Please fix this if you can think of a better regex.
        """,
        __default_value__={"__(.*)__"})

    def __init__(self, text, *args, **kwargs):
        """..."""
        if text:
            if not isinstance(text, (str, Path)):
                raise TypeError(
                    """
                    Bad type {} to construct `TemplateTaggedString` from.
                    Argument `text` should be a string containing the text,
                    or path to the file containing intended text.
                    """.format(type(text)))
            if isinstance(text, Path):
                with open(text, 'r') as file_text:
                    text = file_text.read()
        self._text = text
        super().__init__(*args, **kwargs)

    @lazyfield
    def lines(self):
        """..."""
        return self._text.splitlines()

    @lazyfield
    def words(self):
        return [
            word for line in self.lines
            for word in line.split()]


    @staticmethod
    def trail(regex):
        """Allow trailing punctuation in regex for a word."""
        return r"{}([\W_]*)$".format(regex) 

    @staticmethod
    def decode(regex, word, namespace=None):
        """..."""
        match = re.match(regex, word)
        if not match:
            return None if namespace else tuple()

        try:
            key, trail = match.groups()
        except ValueError as error:
            raise ValueError(
                """
                Expected a key and trail in {} for regex {}.
                \t {}.
                """.format(word, regex, error))
        return\
            "{}{}".format(namespace.get(key, NA), trail)\
            if namespace else (key, trail)

    def detag(self, word, namespace=None):
        """
        decode tag words.

        Arguments
        ------------
        word :: A single word string to check.
        namespace ::  a dict that may contain a tag.

        Returns
        ---------
        if namespace is provided, replace the tag in `word` by its value.
        """
        for tag in self.tags:
            decoded = self.decode(self.trail(tag), word, namespace)
            if decoded:
                return decoded
        return None

    def detex(self, word, namespace=None):
        """
        decode tex tags.

        Arguments
        ------------
        word :: A single word string to check.
        namespace ::  a dict that may contain a tag.

        Returns
        ---------
        if namespace is provided, replace the tag in `word` by its value.
        """
        for cmd in self.cmds_latex:
            if word.startswith(cmd):
                query = word[len(cmd):]
                assert query[0] == '{',\
                    "first char in query {}: {}".format(query, query[0])
                decoded = self.decode(self.trail(r"{(.*)}"), query, namespace)
                if decoded:
                    return decoded
        return None

    def lookup(self, word, namespace=None):
        """
        Look through the provided namespace.
        """
        detaged = self.detag(word, namespace)
        if detaged:
            return detaged if namespace else detaged[0]
        detexed = self.detex(word, namespace)
        if detexed:
            return detexed if namespace else detexed[0]
        return word if namespace else None

    @lazyfield
    def keys(self):
        """
        words in self that may be keys.
        """
        return[
            word for word in (
                self.lookup(word) for word in self.words)
            if word]

    def format(self, **namespace):
        """
        Fill this template

        Argument
        ---------
        namespace_lookup :: A dict
        """
        if not self._text:
            return self._text

        return\
            '\n'.join(
                ' '.join(self.lookup(word, namespace) for word in line.split())
                for line in self.lines)
