"""Circuit composition measurements for Blue Brain circuits."""

from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.models.bluebrain import utils

class CellDensityMeasurement(measurement.Method):
    """..."""

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit

    label = "cell_density"
    phenomenon = Phenomenon("cell_density", "Number of cells in a unit volume")

    def __call__(self, roi):
        """Number of cells in a unit volume, [1000/mm^3]"""
        return 1.e-3 * self.__circuit.stats.cell_density(roi)


class CellRatioMeasurement(measurement.Method):
    """..."""

    label = "cell_ratio"
    phenomenon = Phenomenon("cell_ratio",
                            "Fraction of inhibitory cells in the circuit.")

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit

    def __region_cell_counts(self, roi):
        """Counts of inhibitory and excitatory cells, in a region of interest,
        as a pandas Series."""
        p0, p1 = roi.bbox
        query = {Cell.X: (p0[0], p1[0]),
                 Cell.Y: (p0[1], p1[1]),
                 Cell.Z: (p0[2], p1[2]) }
        props = [Cell.X, Cell.Y, Cell.Z, Cell.SYNAPSE_CLASS]
        cells = circuit.cells.get(query, props)
        cells_inh = cells[cells.synapse_class == "INH"]
        cells_exc = cells[cells.synapse_class == "EXC"]

        inh_in_roi = roi.contains(cells_inh[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_inh_count = np.count_nonzero(inh_in_roi)

        exc_in_roi = roi.contains(cells_exc[[Cell.X, Cell.Y, Cell.Z]].values)
        roi_exc_count = np.count_nonzero(exc_in_roi)

        return pd.Series({"INH": roi_inh_count,
                          "EXC": exc_in_roi,
                          "TOT": roi_exc_count + roi_inh_count})

    def __call__(self, roi):
        """Ratio of the number of inhibitory cells to
        the number of excitatory cells in a region of interest (roi)
        of the circuit.
        """
        ccounts = self.__region_cell_counts(roi)
        return (1.0 + ccounts['INH']) / (1.0 + ccounts['EXC'])
    
class InhibitorySynapseRatioMeasurement(measurement.Method):
    """..."""

    label = "inhibitory_synapse_density"

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit

    def __call__(self, roi):
        """Count the number of inhibitory synapses within a
        region of interest (roi), and divides the number by the roi's volume.
        """
        utils.synapse_density(circuit, roi, 'INH', scale_factor=1.e-9)       

class ExtrinsicIntrinsicSynapseDensityMeasurement(measurement.Method):
    """..."""

    label =  "synapse_density"

    _spine_density_per_unit_length = Record(mean = 1.05, std = 0.35)

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit

    def __call__(self, roi):
        """Compute the expected synapse density
        in a region of interest (roi) of the
        circuit by multiplying the total dendrite
        length in the roi with the known synapse
        density per unit length.
        """
        mean = self._spine_density_per_unit_length.mean
        stdev = self._spine_density_per_unit_length.stdev

        return utils.spine_count_density(circuit, roi,
                                         spine_density_per_unit_len_mean=mean,
                                         spine_density_per_unit_len_stdev=stdev)
