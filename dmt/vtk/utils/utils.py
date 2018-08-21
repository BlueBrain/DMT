"""General utilities."""

import collections

def isabstract(cls):
    """is the class cls abstract?"""
    return (hasattr(cls, '__abstractmethods__') and
            isinstance(cls.__abstractmethods__, collections.Iterable) and
            len(cls.__abstractmethods__) > 0)


def get_file_name_base(file_name=None):
    """Get the base from a file name, stripping away it's suffix."""
    return ("report" if file_name is None else
            '_'.join(file_name.split('.')[0:-1]).strip().replace(' ', '_'))
