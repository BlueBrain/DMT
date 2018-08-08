"""Tests for class Field."""

from dmt.vtk.utils.descriptor import Field, initialize_fields

@initialize_fields
class TestField:
    """A class to test fields."""
    i = Field(
        __name__ = "i",
        __type__ = int,
        __doc__  = """An integer value that must be an integer"""
    )
    j = Field(
        __name__ = "j",
        __type__ = int,
        __is_valid_value__ = lambda i: i < 0,
        __doc__ = """An integer, must be negative"""
    )
    f = Field(
        __name__ = "f",
        __type__ = float,
        __is_valid_value__ = lambda i: i > 0.0,
        __doc__ = """A field that must always be positive."""
    )
