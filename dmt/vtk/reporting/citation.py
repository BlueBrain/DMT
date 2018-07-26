"""Citation"""

class Citation:
    """Citation is POD entity.
    ----------------------------------------------------------------------------
    Implementation Note
    ----------------------------------------------------------------------------
    This first implementation is a stub,
    that can be made richer and useful...
    """
    def __init__(self, citation_string):
        """citation_string should be a string"""
        self.__value = citation_string

    def __repr__(self):
       return self.__value
