"""example usage of units"""

import unittest
from unittest import TestCase
from dmt.measurement.units import Meter, Kilometer
from dmt.quantity.base_quantity import Length

class LengthUnits(TestCase):
    """test units for length"""

    def test_conversion(self):
        kms = Length(magnitude=1.0, unit=Kilometer)
        ms = kms.convert_unit(to=Meter)
        self.assertTrue(ms.magnitude == 1000.0)
        kms2 = ms.convert_unit(to=Kilometer)
        self.assertTrue(kms2.magnitude == 1.0)
