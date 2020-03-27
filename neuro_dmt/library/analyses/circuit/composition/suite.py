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

from ..import *

LOGGER = Logger(client=__file__)

class CompositionAnalysisSuite(WithFields):
    """
    Analyze the composition of a brain circuit model.
    """
    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=100)
    size_roi = Field(
        """
        Size of ROIs that composition phenomena will be computed in.
        """,
        __default_value__=50. * np.ones(3))
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.path.join(os.getcwd(), "reports"))
    morphologies_interneurons = Field(
        """
        Interneuron morphologies that are stained by markers",
        """,
        __default_value__=[
            "BP", "BTC", "CHC", "DB", "LBC", "NBC", "MC", "SBC", "SSC"])],
    number_cortical_thickness_bins = Field(
        """
        Number of bins for by depth or by height analyses.
        """,
        __default_value__=50))
