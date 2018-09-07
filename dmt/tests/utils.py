"""Utilities releveant for testing."""
import os

class TestEnv:
    """Put relevant paths for testing."""
    def __init__(self, dmt_path, *args, **kwargs):
        """Only one relevant path for us, the path to the local installation
        of DMT."""
        self.DMTPATH = dmt_path
        self.DMTDATASETPATH\
            = kwargs.get("dmt_datasetpath",
                         os.path.join(dmt_path, "examples", "datasets"))
                                                      


