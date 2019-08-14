"""
A figure is a graphic with a caption.
"""

from dmt.tk.field import Field, lazyproperty, WithFields

class Figure(WithFields):
    """
    A `Figure` is a graphic with a caption.
    """
    graphic = Field(
        """
        A PDF, PNG, or any other format.
        """)
    caption = Field(
        """
        A text to go with the graphic.
        """)

    def __init__(self,
                 figure_graphic,
                 caption="No caption provided",
                 *args, **kwargs):
        """
        Initialize with graphic as an argument.
        `WithField` provides an `__init__` method that accepts initializer
        arguments as keyword arguments.
        However, with this `__init__` method we cannot pass the graphic as a
        keyword argument.

        We still allow `*args, **kwargs` that will allow `class Figure` to be
        mixed in some other class.
        """
        super().__init__(
            graphic=figure_graphic,
            caption=caption,
            *args, **kwargs)


    def save(self, path, dpi=100):
        """
        Save the figure.
        """
        return self.graphic.savefig(path, dpi=dpi)
