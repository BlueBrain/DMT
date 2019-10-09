"""
Test develop field descriptors.
"""
import numpy as np
from .. import LambdaField, Field, WithFields

def test_lambda_field():
    """
    LambdaField should allow lazy fields defined on other self attrs.
    """
    class Position(WithFields):
        x = Field("x")
        y = Field("y")
        z = Field("z")
        radial = LambdaField(
            """
            radial position
            """,
            lambda self: np.linalg.norm([self.x, self.y, self.z]))
        jinga = LambdaField(
            """
            bad lazy field
            """,
            1)


    p = Position(x=1, y=1, z=1)
    assert p.radial == np.sqrt(p.x ** 2 + p.y ** 2 + p.z ** 2)
    assert p.jinga == 1

