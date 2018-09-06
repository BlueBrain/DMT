import os

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
