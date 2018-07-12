"""Units of mass."""

from dmt.dmt.measurement.units import Unit

class Gram(Unit):
    """Gram is the standard unit used to measure mass."""

    label = "g"

    scale_factor = 1.0


class Kilogram(Unit):
    """1000 grams"""

    label = "kg"

    scale_factor = 1.e3


class Milligram(Unit):
    "1/1000 grams"

    label = "mg"

    scale_factor = 1.e-3
