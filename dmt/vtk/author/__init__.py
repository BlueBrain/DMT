"""Author is anyone who has either
1. provided data, with it's meta-data, or
2. written a loader (adapter) for a data-set,
3. provided a model adapter,
4. written a final validation, combining each of the above.

Author information can be used for querying for data / models / or tests,
and for creating a home-page for the author.

We will allow an Entity's Author to be a list --- after all, most projects
are done in collaboration.
"""
import numpy as np

class Author:
    """Author of an artefact.

    Implementation Notes
    --------------------------------------------------------------------
    While the implementation below is explicit,
    we should be able to abstract away such details into something like
    vtk.utils.collections.Record
    --------------------------------------------------------------------
    """
    def __init__(self,
                 name="Anon Y Mouse ",
                 affiliation="Unik N Oun",
                 user_id=0):

        self.__name = name
        self.__affiliation = affiliation
        self.__user_id = user_id


    @property
    def name(self):
        return self.__name

    @property
    def affiliation(self):
        return self.__affiliation

    @property
    def user_id(self):
        return self.__user_id

    @property
    def homepage(self):
        return "https://www.dmt.org/users/{}".format(self.__user_id)

    def __repr__(self):
        """represent an Author, on the screen."""
        return """Author(
        name: {},
        affiliation: {},
        homepage: {}
        )""".format(self.name, self.affiliation, self.homepage)

    
#cannot create an Author inside the class body, so
Author.anonymous = Author()
Author.zero = Author(name = "V. Sood",
                     affiliation = "BBP, EPFL",
                     user_id = 0)
Author.one  = Author(name = "H. Dictus",
                     affiliation = "BBP, EPFL",
                     user_id = 1)
