import pandas as pd
from dmt.analysis import Analysis
from dmt.model.interface import interfacemethod
from neuro_dmt.library.composition import SimpleValidation
from neuro_dmt.library.composition.utils import columns


class CellDensityValidation(SimpleValidation):
    """validate cell density"""

    measurement = "cell_density"

    # wrapper because python is bizarre
    # TODO: make it work like it should
    def plotter(self, *args, **kwargs):
        return columns(*args, **kwargs)


    @interfacemethod
    def cell_density(adapter_self, query):
        """
        return the cell density of the adapted model
        for parameters specified by query
        """
        pass


class INHRatioValidation(CellDensityValidation):

    measurement = "inhibitory_ratio"

    def __call__(self, adapted):
        measured = [adapted.cell_density(dict(**q, sclass='INH'))
                    / adapted.cell_density(q)
                    for q in self.by]
        return self.write_report(measured)
