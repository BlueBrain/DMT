"""interfaces for classes for input / output."""

from zope.interface import Interface, Attribute, implementer

class SupportsSavingFiles(Interface):
    """Behavior of a class that supports saving files."""
    def get_output_dir(self, *args):
        """figure out what typical args are, what their types should be,
        and what the return type of this function should be."""
        pass
