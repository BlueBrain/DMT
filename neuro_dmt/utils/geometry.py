"""
Generic, utilities to handle geomtries.
"""

from dmt.tk.field import Field, lazyfield, WithFields

class Interval(WithFields):
    """
    An `Interval` is two floats.
    """
    bottom = Field(
        """
        The bottom of the interval.
        """)
    top = Field(
        """
        The top of the interval,.
        """)

    @lazyfield
    def thickness(self):
        """
        Thickness is the length of the this `Interval`.
        """
        return self.top - self.bottom

