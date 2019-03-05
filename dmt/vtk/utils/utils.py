"""General utilities."""
import collections
import time
from dmt.vtk.utils.collections import Record

def isabstract(cls):
    """is the class cls abstract?"""
    return (hasattr(cls, '__abstractmethods__') and
            isinstance(cls.__abstractmethods__, collections.Iterable) and
            len(cls.__abstractmethods__) > 0)

def get_file_name_base(
        file_name=None):
    """Get the base from a file name, stripping away it's suffix."""
    if file_name is None:
        return "report"
    fname_parts = file_name.split('.')
    if len(fname_parts) == 1:
        return fname_parts[0].strip().replace(' ', '_')
    return '_'.join(fname_parts[0:-1]).strip().replace(' ', '_')

def get_file_name(
        some_string,
        is_illegal=lambda character: character in {' ', ',', '~', '/', ';', ':'},
        replacement_character='_'):
    "convert a string into a name suitable for a file. "
    return\
        replacement_character.join(
            ' '.join(
                ' ' if is_illegal(character) else character
                for character in some_string)\
            .split())

def grouped_label(*args):
    """Create a label for a group of things each of which has a label."""
    try:
        things = sorted(args, key=lambda thing: thing.label)
        return '_'.join(thing.label for thing in things)
    except AttributeError:
        return "label"

get_label = grouped_label #an alias

def timestamp(now=None, sep=None):
    """stamp for saving..."""
    def two_char(s):
        """Make string 's' at least two characters long."""
        s = str(s)
        return s if len(s) >= 2 else ("0{}".format(s) if len(s) == 1 else "00")
    now = now if now else time.localtime()
    ts = Record(
        day="{}{}{}".format(
            two_char(now.tm_year),
            two_char(now.tm_mon),
            two_char(now.tm_mday)),
        time="{}{}{}".format(
            two_char(now.tm_hour),
            two_char(now.tm_min),
            two_char(now.tm_sec)) )
    return "{}{}{}".format(ts.day, sep, ts.time) if sep else ts
