"""
Statistical utilities.
"""

from abc import abstractmethod
from dmt.tk.field import Field, LambdaField, ABCWithFields

class Statistics(ABCWithFields):
    """
    Base class to obtain statistics for data.
    """
    evaluator = Field(
        """
        A callable that accepts measurement data and returns a statistical
        summary, for example, as a `pandas.DataFrame`.
        This attribute may also be implemented as a method in a subclass.
        """)
    story = Field(
        """
        Description of the statistical method used.
        """,
        __default_value__="Not Provided")

    def __init__(self, evaluator, **kwargs):
        """..."""
        super().__init__(
            evaluator=evaluator,
            **kwargs)

from .distributions import *
