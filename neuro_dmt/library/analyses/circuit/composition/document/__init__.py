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
Document composition analysis.
"""

from dmt.analysis.document.builder import DocumentBuilder


def get(*args, **kwargs):
    """

    A document will consist of chapters.
    Each chapter is saved in it's own folder ---
    resources for a chapter can thus be stored in it's directory.

    TODO: Write a complete chapter before figuring how to include it here.
    """
    document = DocumentBuilder("Composition")

    @document.chapter
    def layer_thickness():
        """
        The neocortex consists of layers of cells. Here we analyze how
        layer thicknesses vary over a brain region.
        """
        from .layer_thickness import get
        return get(*args, **kwargs)
