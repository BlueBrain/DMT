"""
Adapter interfaces that document what is required of adapters to use
our suite of analyses.
"""

from dmt.model.interface import Interface


class CellDensityAdapterInterface(Interface):
    """
    This class documents the methods that must be adapted for your circuit
    model to use cell density analyses.
    """

    __measurement__ = "cell_density"

    def get_label(self,
            circuit_model):
        """
        A label that can be used to name a pandas.DataFrame column.
        """
        raise NotImplementedError

    def get_cell_density(self,
            circuit_model,
            mtype=None,
            etype=None,
            region=None,
            layer=None):
        """
        Get number of cells in a unit volume in the circuit represented by
        `circuit_model`.

        Implementation Guideline
        -------------------------
        Cell density must be measured for the values of parameters passed
        as keyword arguments. For example the invocation,

        `model_adapter.get_cell_density(`
        ~   `mtype=L23_MC,`
        ~   `region='SSp',`
        ~   `layer=1)`

        should return the density of L23_MC cells in layer 1 of the primary
        somatosensory cortex.

        The implementation may compute:
        1. the mean density sampled over the space implied by the parameters
        ~  passed
        2. the mean density in a randomly selected volume in the confines of
        ~  of the physical space implied by the parameters passed.

        Arguments
        -------------------
        `circuit_model`: model of a brain circuit
        `mtype`: The morphology type of the cells to compute density for.
        `etype`: The electric type of the cells to compute density for.
        `layer`: The layer in which the cells should be counted.
        `region`: The brain region in which cells should counted.


        If a parameter is not specified, then cells should be counted in all
        possible values of that parameter. For example, if `layer` is None (or
        not passed), cell density should be computed over all the layers.

        How this method's result will be used
        ---------------------------------------
        A sample of cell densities will be collected by calling this method
        multiple times, for each combination of the spatial parameters 
        (`region`, `layer`) as well as cell-type parameters (`etype`, `mtype`).

        Our preferred adapter would be a random sampler over space implied
        by the spatial parameters. However, our code should be able to prepare 
        an analysis if your adapter computes mean values over the entire 
        spatial volume implied by the spatial parameters.


        Returns
        ------------------
        a float value
        """
        raise NotImplementedError


