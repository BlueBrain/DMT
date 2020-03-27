# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

from collections import OrderedDict
import numpy as np
import pandas as pd
import numpy.testing as npt
import pytest as pyt
import matplotlib
import matplotlib.pyplot as plt
from dmt.tk.enum import MEAN, STD
from dmt.tk.plotting.circle import CircleTool, CirclePlot


def assert_nested_dicts_approx_equal(d1, d2):
    if not isinstance(d1, dict):
        assert d1 == pyt.approx(d2)
        return
    d1k = sorted(d1.keys())
    assert d1k == sorted(d2.keys())
    for k in d1k:
        assert_nested_dicts_approx_equal(d1[k], d2[k])
    return


class TestCircleTool:
    """test the geometric helper CircleTool"""

    def test_angles_to_points(self):
        """test conversion of clockwise angles from [0, 1] to
        cartesian coordinates"""
        unitcircle = CircleTool(1.0)
        npt.assert_array_equal(unitcircle.angles_to_points(0), [0, 1])
        npt.assert_array_equal(unitcircle.angles_to_points([0]), [[0, 1]])
        npt.assert_array_almost_equal(unitcircle.angles_to_points(
            [np.pi/2, np.pi]), [[1, 0], [0, -1]])

    def test_segment_points(self):
        """test getting N points between two angles on the circle"""
        unitcircle = CircleTool(1.0)

        def assert_points_at_angles(points, angles):
            npt.assert_array_equal(points[:, 0],
                                   np.sin(angles) * unitcircle.radius)
            npt.assert_array_equal(points[:, 1],
                                   np.cos(angles) * unitcircle.radius)

        npt.assert_array_equal(unitcircle.segment_points(0, np.pi/4, 0),
                               np.zeros((0, 2)))
        assert_points_at_angles(unitcircle.segment_points(0, np.pi/4, 1),
                                [0])
        assert_points_at_angles(
            unitcircle.segment_points(3 * np.pi / 5, 3 * np.pi / 4, 2),
            [3 * np.pi / 5, 3 * np.pi/4])

        assert_points_at_angles(
            unitcircle.segment_points(np.pi/4, np.pi, 3),
            [np.pi / 4, 5 * np.pi / 8, np.pi])

        drawpoints = unitcircle.segment_points(np.pi/4, 3 * np.pi/4)
        assert_points_at_angles(drawpoints[0:1], [np.pi/4])
        assert_points_at_angles(drawpoints[-1:], [3 * np.pi/4])
        drawpoints = unitcircle.circle_points(100)
        npt.assert_array_almost_equal(
            drawpoints[:, 0]**2 + drawpoints[:, 1]**2, unitcircle.radius)

        npt.assert_array_almost_equal(
            unitcircle.segment_points(2 * np.pi / 3, 0),
            np.flip(unitcircle.segment_points(0, 2 * np.pi / 3), axis=0))

    def test_circle_points(self):
        """test getting a circle consisting of N points"""
        unitcircle = CircleTool(1.0)
        npt.assert_array_equal(unitcircle.circle_points(0),
                               np.zeros((0, 2)))
        npt.assert_array_equal(unitcircle.circle_points(1),
                               [[0., 1.]])
        npt.assert_array_almost_equal(
            unitcircle.circle_points(2),
            [[0., 1.], [0., 1.]])
        npt.assert_array_almost_equal(
            unitcircle.circle_points(5),
            [[0., 1.], [1., 0.], [0., -1.], [-1, 0], [0., 1.]])
        drawpoints = unitcircle.circle_points(100)
        npt.assert_array_almost_equal(
            drawpoints[:, 0]**2 + drawpoints[:, 1]**2, unitcircle.radius)

    def test_curve_points(self):
        """test getting N points drawing a curve inside the circle
        from one angle to another"""
        unitcircle = CircleTool(1.0)
        pts = unitcircle.curve_points(0, np.pi/2)
        start = pts[0]
        end = pts[-1]
        npt.assert_array_almost_equal(start, [0, 1])
        npt.assert_array_almost_equal(end, [1, 0])
        N = 10
        npt.assert_array_almost_equal(
            unitcircle.curve_points(0, np.pi, N=N),
            np.array([(0, p) for p in np.linspace(1, -1, N)]))

    # TODO: test and implement curve_polygon
    def test_curve_polygon(self):
        """test generate a matplotlib polygon for a particular curve"""
        unitcircle = CircleTool(1.0)
        f1, f2, t1, t2 = np.pi/2, 3 * np.pi / 4, np.pi, 8 * np.pi / 7
        poly = unitcircle.curve_polygon(f1, f2, t1, t2)
        npt.assert_array_equal(np.concatenate(
            [unitcircle.curve_points(f1, t1),
             unitcircle.segment_points(t1, t2),
             unitcircle.curve_points(t2, f2),
             unitcircle.segment_points(f2, f1)]),
                               poly.get_xy())

    def test_segment_polygon(self):
        """test generate a matplotlib polygon for a segment"""
        unitcircle = CircleTool(1.0)
        angle1, angle2 = 2 * np.pi/3, np.pi
        width = 0.01
        outer = CircleTool(1 + width)
        inner_points = unitcircle.segment_points(angle1, angle2)
        npt.assert_array_almost_equal(
            unitcircle.segment_polygon(angle1, angle2, width).get_xy(),
            np.concatenate([
                inner_points,
                outer.segment_points(angle2, angle1),
                [inner_points[0]]]))


# TODO: parameterize column to plot (MEAN)
# TODO: docstrings on all tests
# TODO: many of these tests test things that do not need to be public methods
#       this is only because the public interface (.plot) returns such an
#       untestable object, so we need to test the methods that create it
#       this is not ideal, need a way to test plot output
#       TODO: maybe have a __plot_components__ function that outputs all then
#             patches and labels and components that make up the plot
#             s.t. plot just assembles these into a figure, making
#             __plot_components__ the testable interface
# TODO: technically I should mock CircleTool for this.
class TestCirclePlot:
    """
    test CirclePlots
    remember that the real test will have to be manual
    """

    def test_more_nondata_cols(self):
        """
        if there are more than two columns which may contain
        group parameters, raise a ValueError
        """
        df = pd.DataFrame({
            MEAN: [1, 2],
            'a': [1, 2],
            'b': [2, 3],
            'c': [4, 5]})
        with pyt.raises(ValueError):
            CirclePlot().plot(df)

    def test_no_MEAN(self):
        """
        if there is no MEAN column, we cannot plot. raise a ValueError
        """
        df = pd.DataFrame({
            'a': [1, 2],
            'b': [2, 3]})
        with pyt.raises(ValueError):
            CirclePlot().plot(df)

    def test_assign_group_labels(self):
        """
        test using a callback to create custom group labels
        """
        df = pd.DataFrame(OrderedDict([
            (('a', 'b'), ['1', '2']),
            (('a', 'c'), ['3', '4']),
            (('g', 'f'), ['5', '6']),
            ((MEAN, ''), [3, 4])]))
        default = CirclePlot().__plot_components__(df)[0]
        assert all([grp == exp for grp, exp in
                    zip(default.keys(), ['1, 3', '2, 4', '5', '6'])])

        custom = CirclePlot(
            value_callback=lambda row: ''.join(row.values))\
            .__plot_components__(df)[0]
        assert all([grp == exp for grp, exp in
                    zip(custom.keys(), ['13', '24', '5', '6'])])

    # TODO: test group order is occurrence not sorted
    class TestGroupAngles:
        """test that the locations of group patches
        are being placed correctly"""

        def test_group_angles(self):
            """
            test basic with two groups,
            patch size should be proportional to the number of
            connections to and from a group
            groups start at top of circle, an show clockwise in order
            of occurrence in the 'from' column
            """
            df = pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, 2]})
            plotter = CirclePlot()
            group_angles = plotter.__plot_components__(df)[2][0]

            exp_angles = {'a': (0, 5/6 * np.pi),
                          'b': (5/6 * np.pi, 12/6 * np.pi)}

            for f in ['a', 'b']:
                assert group_angles[f] == pyt.approx(exp_angles[f])

        def test_group_angles_NaN(self):
            """test that nan is treated as 0 in terms of group size"""
            df = pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, np.nan]})
            plotter = CirclePlot()
            group_angles = plotter.__plot_components__(df)[2][0]

            exp_angles = {'a': (0, 5/4 * np.pi),
                          'b': (5/4 * np.pi, 8/4 * np.pi)}

            for f in ['a', 'b']:
                assert group_angles[f] == pyt.approx(exp_angles[f])

        def test_group_angles_asymmetric(self):
            """groups that only show up in 'to' column should occur
            after (clockwise of) the groups occurring in 'from'"""
            df = pd.DataFrame(OrderedDict([
                (MEAN, [1, 2]),
                ('pre', ['a', 'b']),
                ('post', ['c', 'c'])]))
            plotter = CirclePlot()
            group_angles = plotter.__plot_components__(df)[2][0]
            print(*group_angles.keys())
            exp_angles = {'a': (0, 1/3 * np.pi),
                          'b': (1/3 * np.pi, 3/3 * np.pi),
                          'c': (3/3 * np.pi, 6/3 * np.pi)}

            for f in ['a', 'b']:
                assert group_angles[f] == pyt.approx(exp_angles[f])

        def test_group_angles_space(self):
            """check that the size of groups shrinks appropriately when
            spaces are put between them"""
            df = pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, 2]})
            plotter = CirclePlot(space_between=np.pi / 4)
            group_angles = plotter.__plot_components__(df)[2][0]
            unit_size = 1.5 / 12
            exp_angles = {'a': (np.pi/8, (1/8 + 5 * unit_size) * np.pi),
                          'b': ((5 * unit_size + 3/8) * np.pi,
                                (2 - 1/8) * np.pi)}

            for f in ['a', 'b']:
                assert group_angles[f] == pyt.approx(exp_angles[f])

        def test_overlarge_space_between(self):
            """If the space_between groups is too large to plot the
            image, raise a ValueError"""
            df = pd.DataFrame({
                'pre: mtype': ['a', 'a', 'c', 'g'],
                'post: mtype': ['a', 'b', 'a', 'd'],
                MEAN: [1, 2, 1, 2]})

            with pyt.raises(ValueError):
                CirclePlot(space_between=np.pi)

            with pyt.raises(ValueError):
                CirclePlot(space_between=np.pi/2).__plot_components__(df)[2][0]

    class TestColors:
        """test the colors assigned to patches"""

        def test_default_and_custom(self):
            """
            the default colors should use the matplotlib default cm
            but passing a callback should allow overriding this
            """

            df = pd.DataFrame(OrderedDict([
                (('pre', 'mtype'), ['L23_MC', 'L23_PC', 'L4_MC', 'L4_PC']),
                (('pre', 'sclass'), ['INH', 'EXC', 'INH', 'EXC']),
                (('pre', 'layer'), ['L2', 'L2', 'L4', 'L4']),
                (('post', 'mtype'), ['L4_MC', 'L23_MC', 'L4_PC', 'L23_PC']),
                (('post', 'sclass'), ['INH', 'INH', 'EXC', 'EXC']),
                (('post', 'layer'), ['L4', 'L2', 'L4', 'L2']),
                (('mean', ''), [1, 2, 3, 4])]))
            default_colors = CirclePlot().__plot_components__(df)[2][1]
            default_cmap = matplotlib.cm.get_cmap()
            assert default_colors == {
                'L23_MC, INH, L2': {'color': default_cmap(0.)},
                'L23_PC, EXC, L2': {'color': default_cmap(1/3)},
                "L4_MC, INH, L4": {'color': default_cmap(2/3)},
                "L4_PC, EXC, L4": {'color': default_cmap(1.)}}

            cmap = matplotlib.cm.get_cmap('gist_rainbow')

            def custom_color_callback(groups):
                print(pd.DataFrame(list(groups.values())))
                layers = list(pd.DataFrame(list(groups.values())).layer.unique())
                nlayers = len(layers)
                max_color = nlayers - 1
                return {grp: {
                    'color':
                    tuple(
                        v for v in (
                            cmap(layers.index(params['layer']) / max_color)
                            * (np.array([0.5, 0.5, 0.5, 1.0])
                               if params['sclass'] == 'INH' else
                               np.array([1.0, 1.0, 1.0, 1.0]))))}
                        for grp, params in groups.items()}

            grps, _, custom_ptch =\
                CirclePlot(color_callback=custom_color_callback)\
                .__plot_components__(df)[:3]
            custom_colors = custom_ptch[1]
            assert custom_colors == {
                'L23_MC, INH, L2': {'color':
                                    tuple(v * 0.5 if i < 3 else v
                                          for i, v in enumerate(cmap(0.)))},
                'L23_PC, EXC, L2': {'color': cmap(0.)},
                "L4_MC, INH, L4": {'color':
                                   tuple(v * 0.5 if i < 3 else v
                                         for i, v in enumerate(cmap(1.)))},
                "L4_PC, EXC, L4": {'color': cmap(1.)}}

    class TestConnectionAngles:
        """test the angles of the connections between groups"""

        def test_connection_angles(self):
            """basic test for two groups
            connections 'from' a group have their source on the clockwise
            side of the group. Angles 'to' a group have their destination
            on the counterclockwise side of a group. The thickness of a
            connection (the difference in the two source angles, and in
            the two destination angles) is proportional to the strength
            of the connection.
            """
            df = pd.DataFrame(OrderedDict([
                ('pre: mtype', ['a', 'a', 'b', 'b']),
                ('post: mtype', ['a', 'b', 'a', 'b']),
                (MEAN, [1, 2, 1, 2])]))

            plotter = CirclePlot()
            source_angles, dest_angles = plotter.__plot_components__(df)[3]

            exp_source = {'a': {'a': (2/6 * np.pi, 3/6 * np.pi),
                                'b': (3/6 * np.pi, 5/6 * np.pi)},
                          'b': {'a': (11/6 * np.pi, 12/6 * np.pi),
                                'b': (9/6 * np.pi, 11/6 * np.pi)}}

            exp_dest = {'b': {'a': (1/6 * np.pi, 0),
                              'b': (9/6 * np.pi, 7/6 * np.pi)},
                        'a': {'a': (2/6 * np.pi, 1/6 * np.pi),
                              'b': (7/6 * np.pi, 5/6 * np.pi)}}

            assert_nested_dicts_approx_equal(source_angles, exp_source)
            assert_nested_dicts_approx_equal(dest_angles, exp_dest)

        def test_connection_angles_NaN(self):
            """nan connections are not drawn"""
            df = pd.DataFrame(OrderedDict([
                ('pre: mtype', ['a', 'a', 'b', 'b']),
                ('post: mtype', ['a', 'b', 'a', 'b']),
                (MEAN, [1, 2, 1, np.nan])]))

            plotter = CirclePlot()
            source_angles, dest_angles = plotter.__plot_components__(df)[3]

            exp_source = {'a': {'a': (2/4 * np.pi, 3/4 * np.pi),
                                'b': (3/4 * np.pi, 5/4 * np.pi)},
                          'b': {'a': (7/4 * np.pi, 8/4 * np.pi)}}

            exp_dest = {'b': {'a': (1/4 * np.pi, 0)},
                        'a': {'a': (2/4 * np.pi, 1/4 * np.pi),
                              'b': (7/4 * np.pi, 5/4 * np.pi)}}
            assert_nested_dicts_approx_equal(source_angles, exp_source)
            assert_nested_dicts_approx_equal(dest_angles, exp_dest)

        def test_nonsymmetric_groups(self):
            """test that when only receiving connections, all the group's space
            is occupied by the thickness"""
            df = pd.DataFrame(OrderedDict([
                (MEAN, [1, 2]),
                ('pre', ['a', 'b']),
                ('post', ['c', 'c'])]))

            plotter = CirclePlot()
            source_angles, dest_angles = plotter.__plot_components__(df)[3]

            exp_source = {'a': {'c': (0/3 * np.pi, 1/3 * np.pi)},
                          'b': {'c': (1/3 * np.pi, 3/3 * np.pi)}}

            exp_dest = {'a': {'c': (6/3 * np.pi, 5/3 * np.pi)},
                        'b': {'c': (5/3 * np.pi, 3/3 * np.pi)}}

            assert_nested_dicts_approx_equal(source_angles, exp_source)
            assert_nested_dicts_approx_equal(dest_angles, exp_dest)

        def test_exclude_tiny_angles(self):
            """test a parameter which removes small connections from the plot
            """
            plotter = CirclePlot(min_conn_size=np.pi/32)
            df = pd.DataFrame(OrderedDict([
                ('pre: mtype', ['a', 'a', 'b', 'b', 'c',]),
                ('post: mtype', ['a', 'b', 'a', 'b', 'c']),
                (MEAN, [10, 20, 10, 20, np.nan])]))
            src, dst = plotter.__plot_components__(df)[3]
            assert src['c'] == {}
            assert dst['c'] == {}

    class TestPlot:
        """
        very bare-bones checks that the .plot function at least runs
        since the plot consists mostly of PatchCollections we can't really
        test the plot itself
        """

        def test_basic(self):
            df = pd.DataFrame({
                MEAN: [1, 2, 1, 2],
                'pre': ['a', 'a', 'b', 'b'],
                'post': ['a', 'b', 'a', 'b']})
            f, a = CirclePlot().plot(df)
            assert isinstance(f, plt.Figure)
            assert isinstance(a, plt.Axes)
            plt.clf()

        def test_multilevel(self):
            df = pd.DataFrame(OrderedDict([
                ((MEAN, '', '', ''), [1, 2, 1, 2]),
                (('pre', 'm', 'a', 'l'), [1, 1, None, None]),
                (('pre', 'm', 'b', 'l'), [None, None, 2, 2]),
                (('post', 'm', 'a', 'l'), [1, None, 1, None]),
                (('post', 'm', 'a', 'l'), [None, 2, None, 2])]))
            f, a = CirclePlot().plot(df)

            assert isinstance(f, plt.Figure)
            assert isinstance(a, plt.Axes)

        def test_dict_prepost(self):
            """test that it automatically converts to multilevel_dataframe"""
            df = pd.DataFrame({
                MEAN: [1, 2, 1, 2],
                'pre': [{'m': 'a', 'l': 1},
                        {'m': 'a', 'l': 1},
                        {'m': 'b', 'l': 2},
                        {'m': 'b', 'l': 2}],
                'post': [{'m': 'a', 'l': 1},
                         {'m': 'b', 'l': 2},
                         {'m': 'a', 'l': 1},
                         {'m': 'b', 'l': 2}]})
            f, a = CirclePlot().plot(df)

            assert isinstance(f, plt.Figure)
            assert isinstance(a, plt.Axes)
            plt.clf()

        def test_asymmetric(self):
            df = pd.DataFrame({
                MEAN: [1, 2],
                'pre': ['a', 'b'],
                'post': ['c', 'c']})
            f, a = CirclePlot().plot(df)

            assert isinstance(f, plt.Figure)
            assert isinstance(a, plt.Axes)
            plt.clf()

        def test_nan(self):
            df = pd.DataFrame({
                'pre: mtype': ['a', 'a', 'b', 'b'],
                'post: mtype': ['a', 'b', 'a', 'b'],
                MEAN: [1, 2, 1, np.nan]})
            f, a = CirclePlot().plot(df)

            assert isinstance(f, plt.Figure)
            assert isinstance(a, plt.Axes)
            plt.clf()
