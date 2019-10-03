"""
Plotting for DMT
"""
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.data.observation import measurement


golden_aspect_ratio = 0.5 * (1. + np.sqrt(5)) 

def golden_figure(width:int =None, height:int =None):
    """
    Figure with the golden-ratio as its aspect ratio.
    """
    golden_height = 10. if width is None else 2. * width / (1. + np.sqrt(5))
    height = golden_height if height is None else height
    width = golden_aspect_ratio * height if width is None else width

    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)
    return fig, ax


def get_dataframe(data):
    """
    Data may be passed to `Plotter`s as a dict mapping dataset label to
    a dataframe. The `Plotter` needs to convert this data into a
    single dataframe.

    Arguments
    ------------
    `data`: pandas.DataFrame or a mapping dataset -> pandas.DataFrame
    """
    return\
        pd.concat([
            dataframe.assign(dataset=dataset)
            for dataset, dataframe in data.items()])\
          .reset_index()

