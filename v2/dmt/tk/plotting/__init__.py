"""
Plotting for DMT
"""
import matplotlib
#matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties


def golden_figure(width:int =None, height:int =None):
    """
    Figure with the golden-ratio as its aspect ratio.
    """
    golden_height = 10. if width is None else 2. * width / (1. + np.sqrt(5))
    height = golden_height if height is None else height
    width = 0.5 * (1. + np.sqrt(5)) * height if width is None else width

    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)
    return fig, ax


