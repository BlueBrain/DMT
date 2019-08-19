import numpy as np
import matplotlib


# TODO: DOCSTRINGS DOCSTRINGS DOCSTRINGS
class CircleTool:

    def __init__(self, radius, center=None, rotation=0):
        if center is None:
            center = np.zeros((2,))
        self.center = center
        self.radius = radius
        self.rot = rotation

    def angles_to_points(self, angles):
        angles = np.array(angles)
        xes = np.sin(angles + self.rot) * self.radius + self.center[0]
        yes = np.cos(angles + self.rot) * self.radius + self.center[1]
        if angles.shape == ():
            return np.array([xes, yes])
        return np.array([xes, yes]).transpose()

    def segment_points(self, from_angle, to_angle, N=50):
        return self.angles_to_points(np.linspace(from_angle, to_angle, N))

    def circle_points(self, N=100):
        return self.segment_points(0, 2 * np.pi, N=N)

    def _arc_circle(self, from_angle, to_angle):
        mn_ngl = (from_angle + to_angle) / 2
        off_ngl = mn_ngl - np.minimum(from_angle, to_angle)
        ctr_ngl = np.pi - 2 * off_ngl
        rot_ngl = np.pi / 2 - np.minimum(from_angle, to_angle)
        L = self.radius / np.cos(off_ngl)
        Lp = self.radius * np.tan(off_ngl)
        c = np.array([np.sin(mn_ngl + self.rot) * L,
                      np.cos(mn_ngl + self.rot) * L]) + self.center
        if from_angle < to_angle:
            return CircleTool(Lp, center=c,
                              rotation=self.rot-rot_ngl), -ctr_ngl
        return CircleTool(Lp, center=c,
                          rotation=self.rot-rot_ngl-ctr_ngl), ctr_ngl

    def curve_points(self, from_angle, to_angle, N=100):
        if np.isclose(np.abs(from_angle - to_angle), np.pi):
            start = self.angles_to_points(from_angle)
            end = self.angles_to_points(to_angle)
            xspace = np.linspace(start[0], end[0], N)
            yspace = np.linspace(start[1], end[1], N)
            return np.array([xspace, yspace]).transpose()

        a, ngl = self._arc_circle(from_angle, to_angle)
        return a.segment_points(0, ngl, N=N)

    def draw(self, N=100, *args, **kwargs):
        from matplotlib import pyplot as plt
        pts = self.circle_points(N=N)
        plt.plot(pts[:, 0], pts[:, 1], *args, **kwargs)

    def curve_polygon(self, from_angle1, from_angle2, to_angle1, to_angle2):
        xy = np.concatenate(
            [self.curve_points(from_angle1, to_angle1),
             self.segment_points(to_angle1, to_angle2),
             self.curve_points(to_angle2, from_angle2),
             self.segment_points(from_angle2, from_angle1)])
        return matplotlib.patches.Polygon(xy, closed=False)


def make_hashable(df, columnlabel):
    # currently assume all entries have the same keys
    dict_column = df[columnlabel]
    keys = dict_column[0].keys()
    cat_column_label = columnlabel + ": " + ", ".join(keys)
    column_values = [", ".join(str(v)
                               for v in d.values())
                     for d in dict_column.values]
    return df.drop(columns=columnlabel).assign(
        **{cat_column_label: column_values}), cat_column_label


class CirclePlot:

    def __init__(self):
        bar_width = 0.01
        self.circle = CircleTool(1.0)
        self.outer = CircleTool(1.0 + bar_width)

    def _prepare_plot(self, df):
        pass

    def plot(self, df):
        pass



# CirclePlot

# xlabel, ylabel are columns to plot by (e.g. pre and post)
# (these are inferred)
# make_hashable these columns
# plot_circle_plot(df.pivot_table(index=x_column, columns=y_column, values=MEAN))
# TODO: how to handle differing coloration by sclass?

# NOTE: for this plotter we certainly do need some data at analysis-composing time.
#       we need to know what to pivot around
#       (e.g. for connectomics 'pre' and 'post')
#       OR: well, do we really? couldn't we just find the two non-data columns
#           and complain if there are more
#       hmm... that seems like the simplest option
#       though presently their order isn't guaranteed, but that is
#       not the plotter's problem, but whoever passed the dataframe
#
#       it would still be best to make it possible to pass these as a kwarg.
# NOTE: default behavior is to infer, but can also pass args at initialization
#       or at plot-time
