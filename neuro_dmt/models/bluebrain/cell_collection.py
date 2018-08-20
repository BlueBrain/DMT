"""Methods on cell collections. """
import numpy as np
from bluepy.v2.enums import Cell
from neuro_dmt.models.bluebrain import geometry
from neuro_dmt.models.bluebrain.geometry import Cuboid

def center_of_mass(cell_collection):
    """Center of mass of a group of cells.

    Parameters
    ----------------------------------------------------------------------------
    cell_collection :: DataFrame #obtained from  bluepy.v2.circuit.Circuit.cells query
    """
    return cell_collection[[Cell.X, Cell.Y, Cell.Z]].mean()

def centered_box(cell_collection, box_shape=np.array([400.0, 100.0, 230.0])):
    """A box of given shape around the center of mass of a cell group

    Parameters
    ----------------------------------------------------------------------------
    cell_collection :: DataFrame #obtained from  bluepy.v2.circuit.Circuit.cells query
    box_shape :: np.ndarray #3D array that specifies the shape of the desired box
    """
    if not isinstance(box_shape, np.ndarray):
        box_shape = np.array(box_shape)

    com = center_of_mass(cell_collection)
    return Cuboid(com - box_shape / 2.0, com + box_shape / 2.0)
                  

def bounds(cell_collection):
    """Bounding box around a cell collection.

    Parameters
    ----------------------------------------------------------------------------
    cell_collection :: DataFrame #obtained from  bluepy.v2.circuit.Circuit.cells query
    """

    minmax = lambda vs: (np.min(vs), np.max(vs))
    x0, x1 = minmax(cell_collection[Cell.X].values)
    y0, y1 = minmax(cell_collection[Cell.Y].values)
    z0, z1 = minmax(cell_collection[Cell.Z].values)
    p0 = np.array([x0, y0, z0])
    p1 = np.array([x1, y1, z1])
    return Cuboid(p0, p1)

def boundary_cutoff_bbox(cell_collection,
                         boundary_offset=np.array([200.0, 0.0, 100.0])):
    """Get a box around the center of cells in 'cell_collection'"""
    group_center = center_of_mass(cell_collection)
    xcenter = group_center[0]
    ycenter = group_center[1]
    zcenter = group_center[2]

    gb0, gb1 = bounds(cell_collection).bbox

    bottom_left = (gb0[0] - xcenter + boundary_offset[0],
                   gb0[2] - zcenter + boundary_offset[2])
    top_right   = (gb1[0] - xcenter - boundary_offset[0],
                   gb1[2] - zcenter - boundary_offset[2])


    # y of center of mass may not be at the geometric center of layer
    dy1 = gb1[1] - ycenter
    dy2 = ycenter - gb0[1]
    dy = np.min((dy1, dy2))

    return geometry.flat_bbox(groupCenter,
                              cross_section=(bottom_left, top_right),
                              thickness=dy - 2. * boundary_offset[1])

