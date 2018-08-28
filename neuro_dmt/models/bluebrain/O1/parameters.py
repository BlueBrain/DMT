"""Parameters used for measurements.
"""
from dmt.vtk.measurement.parameter import Parameter, GroupParameter
from bluepy.geometry.roi import ROI as RegionOfInterest
from neuro_dmt.models.bluebrain import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.geometry import \
    Cuboid, collect_sample, random_location


class CorticalLayer(GroupParameter):
    label = "Layer"
    value_type = int
    _possible_values = [1, 2, 3, 4, 5, 6]
    grouped_type = RegionOfInterest

    def __init__(self, *args, **kwargs):
        """..."""
        super(CorticalLayer, self).__init__(*args, **kwargs)

    @property
    def order(self):
        return self.value

    @property
    def _has_valid_value(self):
        """Is 'value' an accepted value?"""
        return self.value > 1 and self.value < 6

    def __repr__(self):
        if not self.is_valid(self.value):
            raise ValueError("{} is not a valid value of {}"\
                             .format(value, cls))
        return {
            1: "I",
            2: "II",
            3: "III",
            4: "IV",
            5: "V",
            6: "VI"
        }[self.value]

    def sample(self, circuit, target='mc2_Column',
               sampled_box_shape=np.array([50., 50, 50.]),
               sample_size=None):
        """Sample ROIs in this CorticalLayer in circuit 'circuit'.

        Return
        ------------------------------------------------------------------------
        Tuple(value_type, grouped_type)
        """
        helper = BlueBrainModelHelper(circuit=circuit, target=target)

        half_box = sampled_box_shape / 2.
        def get_roi(loc):
            """ROI at location 'loc'."""
            return Cuboid(loc - half_box, loc + half_box)

        layer_bounds = helper.geometric_bounds({'layer': self.value})
        p0, p1 = layer_bounds.bbox
        region_to_explore = Cuboid(p0 + half_box, p1 - half_box)

        return (get_roi(random_location(region_to_explore))
                for _ in range(sample_size))


