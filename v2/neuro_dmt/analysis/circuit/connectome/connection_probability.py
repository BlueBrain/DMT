"""
Analysis of the pathway connection probability.
"""

from dmt.model.interface import Interface
from dmt.analysis import Analysis

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
            region=None,
            *args, **kwargs):
        """
        Plot measurement, that should be a measurement made on the model ---
        however the code will plot any measurement that satisfies requirements
        of the code below.
        """
        
