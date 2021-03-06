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
Author is anyone who has either
1. provided data, with it's meta-data, or
2. written a loader (adapter) for a data-set, or
3. provided a model adapter, or
4. written an analysis / validation, combining each of the above.

Information encoded in an Author instance can be used for querying for
data, models, or tests, as well for creating a home-page for the author.

Most projects are done in collaborations, accordingly we will allow an Entity's
authors to be a List[Author].
"""

import numpy as np
from ..field import Field, WithFields

class Author(WithFields):
    """
    Author of an artefact.
    """

    name = Field(
        __type__=str,
        __doc__="Author's name.",
        __default_value__="Anon Y Mouse")
    affiliation = Field(
        __type__=str,
        __doc__="Name of the institution that the author is affiliated with.",
        __default_value__="Unik N Oun")
    user_id = Field(
        __type__=int,
        __doc__="A user id assigned to the author, in our system.",
        __default_value__=0)
    homepage = Field(
        __type__=str,
        __doc__="Webpage for this author.",
        __default_value__="not-available")

    def __repr__(self):
        """
        Pretty print an Author.
        """
        return """
        {},
        {}"""\
            .format(
                self.name,
                self.affiliation)


Author.anonymous =\
    Author()
Author.zero =\
    Author(
        name = "Vishal Sood",
        affiliation = "Blue Brain Project, EPFL",
        user_id = 0)
Author.one =\
    Author(
        name = "H. T. Dictus",
        affiliation = "Blue Brain Project, EPFL",
        user_id = 1)

