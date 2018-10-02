import os
from dmt.vtk.utils.logging import Logger, with_logging

class TestEnv:
    """Put relevant paths for testing."""
    def __init__(self, dmt_path, *args, **kwargs):
        """Only one relevant path for us, the path to the local installation
        of DMT."""
        self.DMTPATH = dmt_path
        self.DMTDATASETSPATH\
            = kwargs.get("dmt_datasetspath",
                         os.path.join(dmt_path, "examples", "datasets"))
        


test_env_bbp = TestEnv("/gpfs/bbp.cscs.ch/home/sood",
                       "work/validations/dmt")
test_env_bbp_local = TestEnv("~/work/validations/dmt")
test_env_home_local = TestEnv("/home/muchu/work/bbp/work/validations/dmt")


@with_logging(Logger.level.STUDY)
class ExceptionalTest:
    """Test with exceptions throwing failures."""
    def __init__(self, test, source_info=None, throw=True):
        """..."""
        self._test = test
        self._test_info = "TEST {}: {}\n\t".format(test.__name__, test.__doc__)
        self._source_info = "at {}".format(source_info) if source_info else ""
        self._throw = throw

    def run(self, *args, **kwargs):
        """..."""
        try:
            t = self._test(*args, **kwargs)
        except Exception as e:
            self.logger.failure(self._test_info, self._source_info,
                                "Exception {}: \n".format(e.__class__.__name__),
                                "\t{}".format(e))
            if self._throw:
                raise e
        self.logger.success(self._test_info, t.message)


    class Success:
        """..."""
        def __init__(self, msg, *args, **kwargs):
            """..."""
            self._message = msg

        @property
        def message(self):
            return "Success({})".format(self._message)


    class Failure(Exception):
        """..."""
        def __init__(self, msg, *args):
            self.message = msg
            super().__init__(msg, *args)

