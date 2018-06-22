"""Units of volume."""

from dmt.dmt.measurement.units import Unit

class CubicMeter(Unit):
    """Cubic meter is the standard unit of volume."""

    label = "m^3"

    scale_factor = 1.0


class CubicMillimeter(Unit):
    """1mm X 1mm X 1mm."""

    label = "mm^3"

    scale_factor = 1.e-9


class CubicMicroMeter(Unit):
    """1um X 1um X 1um."""

    label = "um^3"

    scale_factor = 1.e-18
