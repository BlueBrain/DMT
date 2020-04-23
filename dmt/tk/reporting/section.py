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
Section in a report.
"""

from collections import defaultdict
from dmt.tk.field import Field, WithFields


class Section(WithFields):
    """
    Section in a report.
    """
    title = Field(
        """
        Title of this section.
        """)
    content = Field(
        """
        A string contaning text for this `Section` instance.
        This string may require formatting, and can hence be treated
        as a template to be filled in...
        """)
    def __init__(self, title, content, *args, **kwargs):
        """
        Initialize with content.

        Arguments
        ---------------
        content :: A string that may require formatting.
        """
        super().__init__(*args, title=title, content=content, **kwargs)

    @classmethod
    def introduction(cls, content):
        """..."""
        return cls("Introduction", content)
    
    @classmethod
    def methods(cls, content):
        """..."""
        return cls("Methods", content)
    
    @classmethod
    def results(cls, content):
        """..."""
        return cls("Results", content)
    
    @classmethod
    def conclusion(cls, content):
        """..."""
        return cls("Conclusion", content)

    @classmethod
    def discussion(cls, content):
        """..."""
        return cls("Discussion", content)

    def __call__(self, description_model={}):
        """
        Generate content of this section using the description provided.
        """
        return {
            "title": self.title,
            "content": self.content\
                .format_map(
                    defaultdict(
                        lambda: "<Not Provided>",
                        description_model))}
