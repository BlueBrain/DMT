"""
Analysis of the pathway connection probability.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.model.interface import Interface
from dmt.analysis import Analysis
from dmt.tk.plotting import golden_figure

class PathwayConnectionProbabilityAnalysis(Analysis):
    """
    Analyze probability of connections by mtype --> mtype pathway.
    """

    class AdapterInterface(Interface):
        """
        Document all the methods needed for analysis.
        """

        def get_pathway_connection_probability(self,
                circuit_model,
                *args, **kwargs):
            """
            Get a statistical summary of the number of synapses between
            pre- and post-synaptic cells in an mtype --> mtype pathway.
            This method must be defined for the model adapter flass that will
            adapt a circuit model to the requirements of this analysis.
            """
            pass


    def plot(self,
            measurement,
            *args, **kwargs):
        """
        Plot heat-map for the  measurement.
        The code will plot any measurement that satisfies its requirements.

        Arguments
        -------------
        measurement :: pandas.DataFrame with a MultiIndex
        with index labels ('pre_mtype', 'post_mtype')
        """
        def __get_value(pre_mtype, post_mtype):
            """
            Get the value for pre-mtype to post-mtype.
            """
            return measurement.loc(pre_mtype, post_mtype)["mean"]\
                if (pre_mtype, post_mtype) in measurement.index\
                   else np.nan

        index_mtypes =\
            sorted(list({
                mtype for tup in measurement.index.values
                for mtype in tup}))
        matrix = np.array([
            [__get_value(pre_mtype, post_mtype)
             for pre_mtype in index_mtypes]
            for post_mtype in index_mtypes])

        xticks_rotation = 90

        xvar = "post_mtype"
        yvar = "pre_mtype"

        figure =\
            golden_figure(
                height=self._height,
                width=self._width)
        axes =\
            figure.add_axes(
                [0.075, 0.125, 0.9, 0.8])
        image =\
            axes.imshow(
                matrix_data,
                interpolation="nearest")

        n_data_points =\
            len(index_mtypes)
        
        axes.set_xlabel(xvar)
        axes.set_xticklabels(
          index_mtypes,
          rotation="vertical",
          size="xx-small")
        axes.set_ylabel(yvar)
        axes.set_yticklabels(
            index_mtypes,
            size="xx-small")
        color_limits =(
            np.nanmin(matrix),
            np.nanmax(matrix))
        image.set_clim(
            color_limits)
        colorbar=\
            plt.colorbar(image)
        return figure


    def get_measurement(self, circuit_model):
        """
        Measure the model.
        We will use adapter methods here.
        """
        return\
            self.adapter\
                .get_pathway_connection_probability(
                    circuit_model)


