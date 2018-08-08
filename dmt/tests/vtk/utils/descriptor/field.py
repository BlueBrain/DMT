"""Tests for class Field."""

from dmt.vtk.utils.descriptor import Field, has_fields

@has_fields
class TestField:
    """A class to test fields."""
    i = Field(
        __type__ = int,
        __doc__  = """An integer value that must be an integer"""
    )
    j = Field(
        __type__ = int,
        __is_valid_value__ = lambda i: i < 0,
        __doc__ = """Another integer, must be negative"""
    )
    f = Field(
        __type__ = float,
        __is_valid_value__ = lambda i: i > 0.0,
        __doc__ = """A float field that must always be positive."""
    )
