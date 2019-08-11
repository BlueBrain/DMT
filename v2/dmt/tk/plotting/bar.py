"""
Bar plot.
"""

import seaborn

def plot(
        data,
        **plotting_parameters):
    """
    A simple forward to seaborn.

    Arguments
    -----------
    plotting_parameters : keyword arguments for the seaborn method used to
    plot.
    """

    return  seaborn\
        .catplot(
            data=data,
            **plotting_parameters)
