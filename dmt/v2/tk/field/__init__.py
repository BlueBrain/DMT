"""
Classes that are Python Descriptors.

Descriptor: An object attribute whose access has been overriden by methods in
the descriptor protocol. The descriptor protocol requires implementation of at
least one of __get__, __set__, and __delete__ methods.

Further reading: https://docs.python.org/3/howto/descriptor.html

"""

from .field import
    Field,\
    WithFields
