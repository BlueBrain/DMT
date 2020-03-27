# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test develop plotting.
"""

import pandas as pd
import numpy as np
from ..bars import Bars


by_layer_summary_1 =\
    pd.DataFrame(
        {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
         ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
        index=pd.Index(range(1,7), name="layer"))
by_layer_summary_2 =\
    pd.DataFrame(
        {("cell_density", "mean"): np.random.uniform(5.e3, 5.e4, 6),
         ("cell_density", "std"): np.random.uniform(1.e2, 1.e3, 6)},
        index=pd.Index(range(1,7), name="layer"))
 
samples =\
    Bars.get_dataframe({
        "one": by_layer_summary_1,
        "two": by_layer_summary_2})
assert isinstance(samples, pd.DataFrame)
assert "dataset" in samples.columns,\
    "samples dataframe {}".format(samples)
assert "one" in samples.dataset.values,\
    "samples dataframe {}".format(samples)
index = samples.index.names
assert len(index) == 1, "{}".format(index)
assert None in index, "{}".format(index)
