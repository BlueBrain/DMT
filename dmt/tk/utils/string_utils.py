# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Little methods to manipulate strings.
"""

def make_text_like(
        string,
        separator,
        with_capitalized_words,
        with_characters_to_remove=[
            ',', ':', '&', '#', '/',
            '\\', '$', '?', '^', ';', '.'],
        keep_original_capitalization=False):
    """
    Turn a string into normal text like.
    Keep only ASCII characters, removing the provided list.
    And capitalize...
    """
    if not isinstance(string, str):
        string = str(string)
    if keep_original_capitalization:
        with_capitalized_words = False
    def __removed(word):
        return ''.join(c for c in word if c not in with_characters_to_remove)

    def __captialzed(word):
        return word.capitalize() if with_capitalized_words else word

    return separator\
        .join(
            __captialzed(
                __removed(
                    word if keep_original_capitalization else word.lower()))
            for word in string.strip().split(' ')
            if len(word) > 0)

def make_name(
        string,
        separator=None,
        keep_original_capitalization=False):
    """
    Make name from a string.
    Unlike a label, a name may have spaces.
    """
    if not isinstance(string, str):
        string = str(string)
    if separator:
        string = string.replace(separator, ' ')
    return make_text_like(
        string,
        separator=' ',
        with_capitalized_words=True,
        keep_original_capitalization=keep_original_capitalization)

def make_label(string, separator='_'):
    """
    Make label from a string.
    A label cannot have any spaces.
    """
    if not isinstance(string, str):
        string = str(string)
    return make_text_like(
        string,
        separator=separator,
        with_capitalized_words=False)
    
def paragraphs(string):
    """
    Convert a (doc-)string into paragraphs, with each paragraph consisting
    of a single line. It is assumed that the input string separates paragraphs
    by at least two line-end `\n` characters.
    """
    if not isinstance(string, str):
        string = str(string)
    return ' '.join(
        paragraph.strip()
        for paragraph in string.split('\n')
    ).split('  ')
