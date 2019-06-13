"""
A variable is named measurable element.
"""

from ..field import\
    ClassAttribute,\
    ClassAttributeMetaBase,\
    Field,\
    WithFields

class Variable(
        WithFields,
        metaclass=ClassAttributeMetaBase):
    """
    A variable is a named measurable element.
    Subclass this Variable base-class with the required ClassAttributes.
    """
    pass

