"""
Utilities to handle colors to plot with.
"""


from collections.abc import Mapping, Callable

class ColorPalette(Mapping):
    """
    A color palette.
    """
    def __init__(self, colors, *args, **kwargs):
        """..."""
        if isinstance(colors, Callable):
            ColorPalette.from_callable(colors, *args, **kwargs)
            return
        if isinstance(colors, dict):
            ColorPalette.from_dict(colors, *args, **kwargs)
            return
        if isinstance(colors, pd.Series):
            ColorPalette.from_dict(colors.to_dict(), *args, **kwargs)
            return
        if isinstance(colors, pd.DataFrame):
            ColorPalette.from_dataframe(colors, *args, **kwargs)
            return
        raise ValueError(
            """
            No handler for colors:
            \t{}
            """.format(colors))

    @classmethod
    def from_callable(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError

    @classmethod
    def from_dataframe(cls, colors, *args, **kwargs):
        """..."""
        raise NotImplementedError
