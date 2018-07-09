"""Test and develop Phenomenon"""

from dmt.phenomenon import Phenomenon

from dmt.phenomenon import Phenomenon

pcd1 = Phenomenon("Cell Density", "Number of cells in a unit volume.")

pcd2 = Phenomenon("Cell density", "Number of cells in a unit Volume.")

pcd3 = Phenomenon("cell density", "number of cells, in a unit: :: Volume:" )

pir1 = Phenomenon("Inhibitory cell ratio",
                  "Ratio of inhibitory cells to all the cells")

print(Phenomenon.get_known_phenomena("cell density"))
