"""
Analyze circuit composition by layer.
"""

from dmt.tk.field import Field, LambdaField, lazyfield
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis

class CompositionAnalysis(BrainCircuitAnalysis):
    """
    Analyze composition of a brain circuit model.
    """
    model = Field(
        """
        The circuit model to be analyzed.
        """)
    adapter = Field(
        """
        Object that adapter the circuit model to this analysis.
        """)

    def _get_cell_density(self):
        raise NotImplementedError

    @Section
    def cell_density(self):
        """
        A circuit model should reproduce experimentally measured cell
        densities. For the mammalian cerebral cortex, the simplest measurement
        to validate against is the cell density of each layer. In this analysis
        we use three experimentally measured reference datasets (see References
        section) to validate layer cell densities of the circuit model.
        """

