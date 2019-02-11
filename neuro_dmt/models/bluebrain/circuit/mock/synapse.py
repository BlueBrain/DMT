"""A mock synapse."""

import numpy as np
from bluepy.v2.enums\
    import Synapse as BBSynapse
from dmt.vtk.utils.collections\
    import Record

class MockSynapse:
    """a mock synapse, has random properties ."""
    def __init__(self,
            pre_cell,
            post_cell,
            index,
            *args, **kwargs):
        """"...
        pre_cell :: pandas Series (or dict)
        post_cell :: pandas Series (or dict)
        """
        self._pre_gid=\
            pre_cell["gid"]
        self._post_gid=\
            post_cell["gid"]
        self._index=\
            index
        self._axonal_delay=\
            Record(
                min=kwargs.get("min_axonal_delay", 0.),
                max=kwargs.get("max_axonal_delay", 1.))


    @property
    def pre_gid(self):
        """..."""
        return self._pre_gid

    @property
    def post_gid(self):
        """..."""
        return self._post_gid

    @property
    def axonal_delay(self):
        """..."""
        return\
            np.random.uniform(
                self._axonal_delay.min,
                self._axonal_delay.max)
