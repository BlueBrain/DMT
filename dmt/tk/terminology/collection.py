"""
Collection of terms.
"""
from dmt.tk.utils.singleton import Singleton


class TermCollection(Singleton):
    """
    A collection of terms.
    """
    @classmethod
    def make_query(cls, **kwargs):
        """
        Make a query from key-word arguments.
        """
        return {
            label: kwargs[label]
            for label in cls.terms
            if label in kwargs}

    @classmethod
    def filter(cls, **query):
        """
        Filter all the query entries that have value `None`.
        """
        return {
            label: value
            for label, value in query.items()
            if label in cls.terms and value is not None}

