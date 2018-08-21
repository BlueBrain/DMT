"""General utilities."""

import collections

def isabstract(cls):
    """is the class cls abstract?"""
    return (hasattr(cls, '__abstractmethods__') and
            isinstance(cls.__abstractmethods__, collections.Iterable) and
            len(cls.__abstractmethods__) > 0)


def get_file_name_base(file_name=None):
    """Get the base from a file name, stripping away it's suffix."""
    if file_name is None:
        return "report"
    fname_parts = file_name.split('.')
    if len(fname_parts) == 1:
        return fname_parts[0].strip().replace(' ', '_')
    return '_'.join(fname_parts[0:-1]).strip().replace(' ', '_')
