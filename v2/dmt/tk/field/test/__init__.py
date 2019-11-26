"""
Test develop field descriptors.
"""
import pytest as pyt
import numpy as np
from .. import LambdaField, Field, WithFields
from ..class_field import ClassField, class_field

def test_lambda_field():
    """
    LambdaField should allow lazy fields defined on other self attrs.
    """
    class Position(WithFields):
        x = Field("x")
        y = Field("y")
        z = Field("z")
        radial = LambdaField(
            """
            radial position
            """,
            lambda self: np.linalg.norm([self.x, self.y, self.z]))
        jinga = LambdaField(
            """
            bad lazy field
            """,
            1)


    p = Position(x=1, y=1, z=1)
    assert p.radial == np.sqrt(p.x ** 2 + p.y ** 2 + p.z ** 2)
    assert p.jinga == 1

def test_class_field():
    """
    ClassField should add documentation to the including class.
    """

    class Example(WithFields):
        """
        Shows use of `ClassField`s
        """
        example_class_field_one = ClassField(
            """
            Example of a ClassField.
            """,
            example_class_field_one = 1)
        example_class_field_two = ClassField(
            """
            Another example of a ClassField.
            """,
            example_class_field_two = 2)
        

    assert Example.example_class_field_one == 1
    assert Example.__doc_for_field__["example_class_field_one"].strip()\
        == "Example of a ClassField."
    egg = Example()
    assert egg.example_class_field_two == 2
    assert Example.__doc_for_field__["example_class_field_two"].strip()\
        ==  "Another example of a ClassField."

    with pyt.raises(TypeError):
        egg.example_class_field_one = 10


def test_class_field_decorator():
    """
    Decorator method class field should be able to create class fields on the
    including class.
    """

    class Example(WithFields):
        """
        Shows use of `class_field`
        """
        @class_field
        def example_class_field_one(cls):
            """
            Example of a ClassField.
            """
            return 1
        @class_field
        def example_class_field_two(cls):
            """
            Another example of a ClassField.
            """
            return 2
    Example.example_class_field_one(Example)
    Example.example_class_field_two(Example)

    egg = Example()
    assert egg.example_class_field_two == 2,\
        egg.example_class_field_two
    assert Example.__doc_for_field__["example_class_field_one"].strip()\
        == "Example of a ClassField."

    assert Example.example_class_field_one == 1,\
        Example.example_class_field_one
    assert Example.__doc_for_field__["example_class_field_two"].strip()\
        ==  "Another example of a ClassField."

    with pyt.raises(TypeError):
        egg.example_class_field_one = 10
