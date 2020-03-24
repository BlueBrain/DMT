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
        name = "V. Sood",
        affiliation = "BBP, EPFL",
        user_id = 0)
Author.one =\
    Author(
        name = "H. T. Dictus",
        affiliation = "BBP, EPFL",
        user_id = 1)

