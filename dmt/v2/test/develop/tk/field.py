"""
Test develop Field.
"""

from dmt.v2.tk.field import\
    Field,\
    WithFields

class Position(WithFields):
    """
    Position in three dimensions.
    """
    X = Field(
        __doc__="""Position X dimension""",
        __type__=float,
        __validation__=lambda x: x >= 0.)
    Y = Field(
        __doc__="""Position Y dimension""",
        __type__=float,
        __validation__=lambda y: y >= 0.)
    Z = Field(
        __doc__="""Position Z dimension""",
        __type__=float,
        __validation__=lambda z: z >= 0.)

    def __init__(self,
            *args, **kwargs):
        """Pass on ton the super class..."""
        super().__init__(
            *args, **kwargs)


def test():
    """
    Initialization of a class based on WithFields 
    """
    assertion_error =\
        "Initialization should not be possible if fields not set in kwargs"
    try:
        position = Position()
        assert False, assertion_error
    except:
        pass

    try:
        position = Position(X=1)
        assert False, assertion_error
    except:
        pass

    try:
        position = Position(X=1.0, Y=2.0)
        assert False, assertion_error
    except:
        pass

    try:
        position = Position(X=1, Y=2.0, Z=3.0)
        assert False,\
            """Initialization should fail because X has the wrong type."""
    except TypeError:
        pass

    try:
        position = Position(X=1.0, Y=2, Z=3)
        assert False,\
            """Initialization should fail because Y has the wrong type."""
    except TypeError:
        pass

    try:
        position = Position(X=1.0, Y=2.0, Z="A")
        assert False,\
            """Initialization should fail because Z has the wrong type."""
    except TypeError:
        pass

    position = Position(X=1.0, Y=1.0, Z=0.0)

    try:
        position.Z = 1
        assert False,\
            """Setting Z to 1 should fail as 1 is not the correct type (float)."""
    except TypeError:
        pass


