from abc import abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.utils.logging import with_logging, Logger

logger = Logger(client = None,
                name="FCABase",
                level=Logger.level.TEST)

class TestFCAX(WithFCA):
    """..."""
    y = Field(
        __name__="y",
        __type__=int,
        __doc__="""Just a number to test FCA."""
    )
    z = Field(
        __name__="z",
        __type__=int,
        __doc__="""Just another number to test FCA."""
    )
    def __init__(self, x=0, *args, **kwargs):
        logger.inform(" initialize TestFCAX with kwargs {}".format(kwargs))
        self.x = x
        super(TestFCAX, self).__init__(*args, **kwargs)

    @property
    def get_x(self):
        """This method call should fail if 'x' has not been set."""
        return self.x

    @property
    def get_y(self):
        """This method call should fail if 'y' has not been set."""
        return self.y

    @property
    def get_z(self):
        """This method call should fail if 'y' has not been set."""
        return self.z


logger.note("TestFCAX(x=1,y=2,z=3) will succeed")
tfcab123 = TestFCAX(x=1,y=2,z=3)

logger.note("TestFCAX(x=1,y=2) will fail")
try:
    tfcab12 = TestFCAX(x=1,y=2)
except TypeError as e:
    logger.error("TypeError: {}".format(e))
    
logger.note("TestFCAX(x=1) will fail")
try:
    tfcab1 = TestFCAX(x=1)
except TypeError as e:
    logger.error("TypeError: {}".format(e))

class TestFCAXY1(TestFCAX):
    """..."""
    y = 1

logger.note("TestFCAXY1(x=1) will fail")
try:
    xy1 = TestFCAXY1(x=1)
except TypeError as e:
    logger.error("TypeError: {}".format(e))

logger.note("TestFCAXY1(x=1, z=2) will succeed")
TestFCAXY1(x=1, z=2)

class TestFCAXY2(TestFCAX):
    """..."""
    z = 2
    def __init__(self, x, y):
        super(TestFCAXY2, self).__init__(x=x, y=y)

logger.note("TestFCAXY2(1, 2) will succeed")

