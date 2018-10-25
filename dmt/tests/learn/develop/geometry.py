"""What is the geometry of the O1 circuit?
What is the shape of the hexagon?"""
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

cells = circuit.cells.get(properties=[Cell.X, Cell.Y, Cell.Z])

dx = cells.x.max() - cells.x.min()
dy = cells.y.max() - cells.y.min()
dz = cells.z.max() - cells.y.min()
