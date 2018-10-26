"""Parameters specialized for the (fake) atlas based circuit."""
from neuro_dmt.measurement.parameter import Column

class HyperColumn(
        Column):
    """A column into a (fake) atlas circuit,
    that passes through all the layers without any bias."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            value_type=str,
            values=["mc{}".format(n) for n in range(7)],
            label="$target",
            *args, **kwargs)
