"""Units of length."""

from dmt.measurement.units import AtomicUnit
from dmt.physical_dimension import PhysicalDimension

class Meter(Unit):
    """Meter is the standard unit used to measure mass."""

    label = "m"

    scale_factor = 1.0


class Kilometer(Unit):
    """1000 meters"""

    label = "km"

    scale_factor = 1.e3


class Millimeter(Unit):
    "1/1000 meters"

    label = "mm"

    scale_factor = 1.e-3

class Micrometer(Unit):
    "1 millionth of a meter."

    label = "um"

    scale_factor = 1.e-6


meter = AtomicUnit()
