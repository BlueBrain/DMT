"""Certain base classes for reporting."""

from abc import ABC, abstractmethod
from dmt.validation import Pronouncement

class CanPlot(ABC):
    """Required behavior of an analysis that can be plotted."""

    @abstractmethod
    def __caption__(self, report):
        """Caption for the plot.

        Parameters
        ----------
        @report :: Pronouncement

        @report should contain relevant information about the analysis.

        Further Development
        -------------------
        
        Notes
        ------
        1. We can provide guidelines to write a Caption. Or we can write a
        method that generates a Caption that combines the Validation's
        experimental and statistical methods, the validated system, and the
        result of the judgment. However the exact language to use will depend
        on the concrete implementation' details.
        
        It may be less flagrant to use Report as the name of the base class that
        provides a report on the analysis / validation,
        instead of Pronouncement."""

        pass

    @abstractmethod
    def __plot__(self, report, **kwargs):
        """Plot something.

        Parameters
        ----------
        @report :: Pronouncement

        @report should contain relevant information about the analysis / validation.

        Further Development
        --------------------
        We have previously observed that bar plots a very common validation
        plot styles. We can implement a Plottable class that plots bars!
        """
        pass


class PlotsBars(CanPlot):
    """Provides functionality to produce a bar plot."""

    pass

class PlotsLines(CanPlot):
    """Provides functionality to produce a line plot."""
    pass
