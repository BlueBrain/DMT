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
Narrative of a document.
"""
from pathlib import Path
from dmt.model.interface import interfacemethod
from dmt.tk.journal import Logger
from dmt.tk.field import\
    field,\
    LambdaField,\
    NA, Record,\
    WithFields
from .template import TaggedTemplateString
from .import DocElem


LOGGER = Logger(client=__file__)


class Narrative(WithFields):
    """
    Mixin to provide text of a `DocElem`.
    """
    def __init__(self, text=NA, **kwargs):
        kwargs["text"] = text
        super().__init__(**kwargs)
    @field.cast(TaggedTemplateString)
    def text(self):
        """
        Either of:
        1. Callable returning a text.
        ~  The arguments of the call are up to the implementation.
        ~  `(adapter, model)` will be passed, along with keyword arguments.
        ~  So the implementation's signature should be:
        ~  `adapter -> model -> *args -> **kwargs -> text`
        2. Text that can be used as a `Cheetah Template`.
        ~  A word prefixed by a `$` tag will be searched in a `searchList`,
        ~  a mapping `tag -> value`.
        ~  This mapping will be generated from `(adapter, model)` passed to
        ~  the `__call__` method or can be passed directly to the `__call__`
        ~  method.
        """
        return NA

    @interfacemethod
    def get_namespace(adapter, model):
        """
        Get a namepsace to fill the text with.
        """
        raise NotImplementedError

    def save(self, value, path_folder):
        """..."""
        try:
            value_narrative = value.narrative
        except AttributeError:
            value_narrative = value

        path_folder = Path(path_folder)
        path_folder.mkdir(parents=False, exist_ok=True)

        path_file = path_folder.joinpath("narrative.txt")

        with open(path_file, 'w') as output_file:
            output_file.write(value_narrative)

        try:
            save_super = super().save
        except AttributeError:
            return path_file

        return save_super(value, path_folder)

    def __call__(self, adapter, model, namespace=None, **kwargs):
        """...Call Me..."""
        if self.text:
            if not namespace:
                namespace = adapter.get_namespace(model)
            try:
                narrative = self.text.format(**namespace)
            except AttributeError:
                narrative = str(self.text)
        else:
            narrative = str(NA)

        try:
            get_record = super().__call__
        except AttributeError:
            if not isinstance(self, DocElem):
                return narrative
            get_record = lambda *args, **kwargs: Record()
        return get_record(
            adapter, model, **kwargs
        ).assign(
            narrative=narrative
        )


