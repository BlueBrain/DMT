"""
Make a circle plot.
"""
"""
Plot heat maps.
"""
from collections import OrderedDict
import itertools
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell, Synapse
from . import golden_aspect_ratio
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from . import get_dataframe
from .figure import Figure


class GraphicCircle(WithFields):
    """
    The circle that will be plotted
    """

    center = Field(
        """
        Center of the circle.
        """,
        __default_value__=np.array([0., 0.]))
    radius = Field(
        """
        Radius of the circle.
        """,
        __default_value__=1.)
    rotation = Field(
        """
        Some kind of rotation, that I do not understand.
        """,
        __default_value__=0.)

    def at(self, angle):
        return self.center + np.array([
            np.sin(angle + self.rotation) * self.radius,
            np.cos(angle + self.rotation) * self.radius])

    def segment_points(self, _from=0., to=2*np.pi, N=100):
        return np.array([
            self.at(angle)
            for angle in np.linspace(_from, to, N)])

    def _arc_circle(self, angle_1, angle_2):
        angle_mean = (angle_1 + angle_2) / 2.
        #mn_ngl = (angle1 + angle2) / 2
        angle_off = angle_mean - np.minimum(angle_1, angle_2)
        #off_ngl = mn_ngl - np.minimum(angle1, angle2)
        angle_center = np.pi - 2 * angle_off
        #ctr_ngl = np.pi - 2 * off_ngl
        angle_rotation = np.pi / 2 - np.minimum(angle_1, angle_2)
        #rot_ngl = np.pi / 2 - np.minimum(angle1, angle2)
        length = self.radius / np.cos(angle_off)
        #L = self.r / np.cos(off_ngl)
        radius_arc = self.radius * np.tan(angle_off);
        #Lp = self.r * np.tan(off_ngl)
        center_arc = self.center + np.array([
            length * np.sin(angle_mean + self.rotation),
            length * np.cos(angle_mean + self.rotation)])
        #c = np.array([np.sin(mn_ngl + self.rot) * L,
        #                 np.cos(mn_ngl + self.rot) * L]) + self.c
        arc_circle =\
            GraphicCircle(
                center=center_arc,
                radius=radius_arc,
                rotation=self.rotation - angle_rotation)\
                if angle_1 < angle_2 else\
                   GraphicCircle(
                       center=center_arc,
                       radius=radius_arc,
                       rotation=self.rotation - angle_rotation - angle_center)
        arc_angle =\
            - angle_center if angle_1 < angle_2 else angle_center

        return arc_circle, arc_angle
        # if angle1 < angle2:
        #     return Circle(c, Lp, rotation=self.rot-rot_ngl), -ctr_ngl
        # return Circle(c, Lp, rotation=self.rot-rot_ngl-ctr_ngl), ctr_ngl

    def arc_points(self, angle_one, angle_two, N=100):
        arc_circle, arc_angle = self._arc_circle(angle_one, angle_two)
        return arc_circle.segment_points(0, arc_angle, N=N)

    def draw(self, N=100, *args, **kwargs):
        pts = self.segment_points(N=N)
        plt.plot(pts[:, 0], pts[:, 1], *args, **kwargs)


class Synaptome(GraphicCircle):
    """
    Plot circuit synaptome in a circle.
    """
    afferent = Field(
        """
        Some data (type to be determined) for afferent connections.
        """)
    efferent = Field(
        """
        Some data (type to be determined) for efferent connections.
        """)
    mtype = Field(
        """
        Mtype to draw.
        """,
        __default_value__="")
    blowup = Field(
        """
        Some sort of factor, to be understood
        """,
        __default_value__=1.5)
    buffer_main = Field(
        """
        buffer_main?
        """,
        __default_value__=0.3)
    coefficient_transparency = Field(
        """
        How transparent should the painting be?
        """,
        (0.0, 1.0))
    color_dict = LambdaField(
        """
        A dict of colors?
        You may provide a dict to initialize.
        If not provided, a value be computed using other attributes of this
        `Synaptome` instance.
        """,
        lambda self: dict([
            (_m, np.random.rand(3) * 0.6)
            for _m in self.data_exc.keys() + self.data_inh.keys()]))
    min_size_label = Field(
        """
        Min size for the labels?
        """,
        __default_value__=0.02)
    min_size_arr = Field(
        """
        Min size of an array?
        """,
       __default_value__=0.02)
    fontsize = Field(
        """
        Fontsize
        """,
        __default_value__=[8, 25])


    @lazyfield
    def eff_aff(self):
        """
        An alias.
        """
        return ("EFF", "AFF") if not self.mtype else (self.mtype, self.mtype)

    def alpha_fun(self, ends_link):
        """
        Alpha for plotting

        Arguments
        ----------
        `ends_link`: Tuple(2, float) for positions(?) of a link.
        """
        length_link =\
            np.abs(np.diff(ends_link))
        alpha =\
            self.coefficient_transparency[0] +\
            length_link * self.coefficient_transparency[1],
        return\
            np.maximum(
                np.minimum(alpha, 1.0),
                0.5)

    @staticmethod
    def get_matches(data, synapse_class):
        """..."""
        return OrderedDict([
            (_a[0], _a[2])
            for _a in data
            if _a[1] == synapse_class])

    @staticmethod
    def __extract_data__(aff, eff, synapse_class):
        """
        Combine afferent and efferent data that matches

        The critical part of the original code:
        ```
         for _a in eff:
             if _a[1] == match:
                 extract.setdefault(_a[0], np.array([0.0, 0.0]))[1] = _a[2]
         return extract
        ```
        """
        afferent_matches =\
            self.get_matches(aff, synapse_class)
        efferent_matches =\
            self.get_matches(eff, synapse_class)
        all_keys =\
            itertools.chain(
                afferent_matches.keys(),
                (efferent_key
                 for efferent_key in efferent_matches.keys()
                 if efferent_key not in afferent_matches))

        def __combined_value(key):
            """
            Combine afferent and efferent values.
            """
            return np.array([
                afferent_matches.get(key, 0.),
                efferent_matches.get(key, 0.)])

        return\
            OrderedDict([(key, __combined_value(key)) for key in all_keys])

    @lazyfield
    def data_excitatory(self):
        """
        Excitatory data.
        """
        return self.__extract_data__(self.afferent, self.efferent, "EXC")

    @lazyfield
    def data_inhibitory(self):
        """
        Inhibitory data.
        """
        return self.__extract_data__(self.afferent, self.efferent, "INH")

    @lazyfield
    def values_efferent_inhibitory(self):
        """..."""
        return [v[1] for v in self.data_inhibitory.values()]

    @lazyfield
    def values_efferent_excitatory(self):
        """..."""
        return [v[1] for v in self.data_excitatory.values()]

    @lazyfield
    def values_afferent_inhibitory(self):
        """..."""
        return [v[0] for v in self.data_inhibitory.values()]

    @lazyfield
    def values_afferent_excitatory(self):
        """..."""
        return [v[0] for v in self.data_excitatory.values()]

    @lazyfield
    def sum_afferent(self):
        """..."""
        return\
            np.sum(self.values_afferent_inhibitory) +\
            np.sum(self.values_afferent_excitatory)

    @lazyfield
    def sum_efferent(self):
        """..."""
        return\
            np.sum(self.values_efferent_inhibitory) +\
            np.sum(self.values_efferent_excitatory)

    @lazyfield
    def sum_excitatory(self):
        """..."""
        return\
            np.sum(self.values_afferent_excitatory) +\
            np.sum(self.values_efferent_excitatory) -\
            np.sum(self.data_excitatory.get(self.mtype, (0., 0.)))

    @lazyfield
    def sum_inhibitory(self):
        """..."""
        return\
            np.sum(self.values_afferent_inhibitory) +\
            np.sum(self.values_efferent_inhibitory) -\
            np.sum(self.data_inhibitory.get(self.mtype, (0., 0.)))

    def __get_space(self, value):
        """..."""
        space_base =\
            2. * np.pi - 4 * self.buffer_main
        return\
            space_base * value\
            /(self.blowup * (self.sum_efferent + self.sum_afferent) +\
              self.sum_excitatory + self.sum_inhibitory)

    @lazyfield
    def space_eff(self):
        """..."""
        space_eff =\
            self.__get_space(self.blowup * self.sum_efferent)
        return (
            -space_eff / 2.0,
            space_eff / 2.0)

    @lazyfield
    def space_exc(self):
        """..."""
        space_exc =\
            self.__get_space((self.sum_excitatory))
        return (
            self.space_eff[1] + self.buffer_main + space_exc,
            self.space_eff[1] + self.buffer_main)

    @lazyfield
    def space_aff(self):
        space_aff =\
            self.__get_space(self.blowup * self.sum_afferent)
        return (
            self.space_exc[0] + self.buffer_main,
            self.space_exc[0] + self.buffer_main + space_aff)

    @lazyfield
    def space_inh(self):
        """..."""
        space_inh =\
            self.__get_space(self.sum_inhibitory)
        return (
            self.space_aff[1] + self.buffer_main + space_inh,
            self.space_aff[1] + self.buffer_main)


    @lazyfield
    def link_starts(self):
        """
        Where do the links start?

        MR's original code
        ```
        def prepare_link_starts(self, vals, nrmlz, lbls, space, prefix, mp, shortcut=None):
            sc_mtype = None
            if shortcut is not None:
                sc_mtype, mp_alt, prefix_alt = shortcut
            delta = space[1] - space[0]
            s = space[0]
            for _vals, _lbls in zip(vals, lbls):
                for _v, _l in zip(_vals, _lbls):
                    if _l == sc_mtype:
                        mp_alt[prefix_alt + _l] = (s + _v * delta / nrmlz, s)
                    else:
                        mp[prefix + _l] = (s, s + _v * delta / nrmlz)
                    s += _v * delta / nrmlz
            return mp
        ```
        """
        def _generator_link_starts(
                values,
                normalization,
                labels,
                space,
                prefix):
            """..."""
            link_length = lambda v: v * (space[1] - space[0])/normalization

            s = space[0]
            for label, value in zip(labels, values):
                snext = s + link_length(value)
                link_start =(
                    "{}{}".format(prefix, label),
                    (s, snext))
                s = snext
                yield link_start

        values_efferent = itertools.chain(
            self.values_efferent_inhibitory,
            self.values_efferent_excitatory)
        labels_efferent = itertools.chain(
            self.data_inhibitory.keys(),
            self.data_excitatory.keys())
        values_afferent = itertools.chain(
            self.values_afferent_excitatory,
            self.values_afferent_inhibitory)
        labels_afferent = itertools.chain(
            self.data_excitatory.keys(),
            self.data_inhibitory.keys())
        return dict(
            itertools.chain(
                _generator_link_starts(
                    values=values_efferent,
                    normalization=self.sum_efferent,
                    labels=labels_efferent,
                    space=self.space_eff,
                    prefix="EFF"),
                _generator_link_starts(
                    values=values_afferent,
                    normalization=self.sum_afferent,
                    labels=labels_afferent,
                    space=self.space_aff,
                    prefix="AFF")))

    @lazyfield
    def link_ends(self):
        """
        Where do links end?
        MR's original code:
        ```
        def prepare_link_ends(self, data, nrmlz, space, mp, sc_mtype=None):
            delta = space[1] - space[0]
            s = space[0]
            for kk in data.keys():
                if kk != sc_mtype:
                    mp['AFF' + kk] = (s, s + data[kk][0] * delta / nrmlz)
                    s = mp['AFF' + kk][1]
                    mp['EFF' + kk] = (s, s + data[kk][1] * delta / nrmlz)
                    s = mp['EFF' + kk][1]
            return mp
        ```
        """
        def _generator_link_ends(
                data,
                normalization,
                space,
                sc_mtype):
            s = space[0]
            link_length = lambda v: v * (space[1] - space[0])/normalization
            for key, value in data.items():
                if key == sc_mtype:
                    continue
                s_aff = s + link_length(value[0])
                s_eff = s_aff + link_length(value[1])
                link_ends =(
                    ("AFF{}".format(key), (s, s_aff)),
                    ("EFF{}".format(key), (s_aff, s_eff)))
                s = s_eff
                yield link_ends

            for link_ends in __end_generator():
                for key_value in link_ends:
                    yield key_value

        return dict(
            itertools.chain(
                self._generator_link_ends(
                    data=self.data_excitatory,
                    normalization=self.sum_excitatory,
                    space=self.space_exc,
                  sc_type=self.mtype),
                self._generator_link_ends(
                    data=self.data_inhibitory,
                    normalization=self.sum_inhibitory,
                    space=self.space_inh,
                    sc_type=self.mtype)))
        

    def __prepare_link_starts(self):
        """
        Where do the links start?
        """
        raise NotImplementedError

    def __prepare_link_ends(self):
        """
        Where do the links end?
        """
        raise NotImplementedError

    def __init__old(self,
            aff,
            eff,
            mtype=None,
            c=np.array([0.0, 0.0]),
            r=1.0,
            blowup=1.5,
            buf_main=0.3,
            transparency_coeff=(0.0, 1.0),
            col_dict=None,
            lbl_min_size=0.02,
            arr_min_sz=0.02,
            fontsize=[8, 25],
            **kwargs):
        super(Synaptome, self).__init__(c, r, **kwargs)
        self.blowup = blowup
        self.buf_main = buf_main
        self.lbl_min_sz = lbl_min_sz
        self.arr_min_sz = arr_min_sz
        self.fontsize = fontsize
        self.eff_aff = ('EFF', 'AFF')
        if mtype is not None:
            self.eff_aff = (mtype, mtype)
        self.alpha_fun =\
            lambda s: np.maximum(
                np.minimum(
                    transparency_coeff[0] + np.abs(
                        np.diff(s)) * transparency_coeff[1],
                    1.0),
                0.05)
        self.prepare_data(aff, eff)
        self.prepare_area(sc_mtype=mtype)

        self.link_starts = {}; self.link_ends = {}
        self.prepare_link_starts(
            [self.vals_eff_inh, self.vals_eff_exc],
            self.sum_eff,
            [self.data_inh.keys(), self.data_exc.keys()],
            self.space_eff,
            'EFF',
            self.link_starts)
        self.prepare_link_starts(
            [self.vals_aff_exc, self.vals_aff_inh],
            self.sum_aff,
            [self.data_exc.keys(), self.data_inh.keys()],
            self.space_aff,
            'AFF',
            self.link_starts,
            shortcut=(mtype, self.link_ends, 'EFF'))
        self.prepare_link_ends(
            self.data_exc,
            self.sum_exc,
            self.space_exc,
            self.link_ends,
            sc_mtype=mtype)
        self.prepare_link_ends(
            self.data_inh,
            self.sum_inh,
            self.space_inh,
            self.link_ends,
            sc_mtype=mtype)
        if col_dict is None:
            self.col_dict =\
                dict([
                    (_m, np.random.rand(3) * 0.6)
                    for _m in self.data_exc.keys() + self.data_inh.keys()])
        else:
            self.col_dict = col_dict


    # def prepare_data(self, aff, eff):
    #     self.data_exc = self.__extract_data__(aff, eff, 'EXC')
    #     self.data_inh = self.__extract_data__(aff, eff, 'INH')
    #     self.vals_eff_inh = [v[1] for v in self.data_inh.values()]
    #     self.vals_eff_exc = [v[1] for v in self.data_exc.values()]
    #     self.vals_aff_inh = [v[0] for v in self.data_inh.values()]
    #     self.vals_aff_exc = [v[0] for v in self.data_exc.values()]

    # def prepare_area(self, sc_mtype=None):
    #     self.sum_aff =\
    #         np.sum(self.vals_aff_inh) + np.sum(self.vals_aff_exc)
    #     self.sum_eff =\
    #         np.sum(self.vals_eff_inh) + np.sum(self.vals_eff_exc)
    #     self.sum_exc =\
    #         np.sum(self.vals_eff_exc) + np.sum(self.vals_aff_exc)
    #     self.sum_inh =\
    #         np.sum(self.vals_eff_inh) + np.sum(self.vals_aff_inh)
    #     self.sum_exc -=\
    #         np.sum(self.data_exc.get(sc_mtype, (0, 0)))
    #     self.sum_inh -=\
    #         np.sum(self.data_inh.get(sc_mtype, (0, 0)))
    #     base_space =\
    #         2 * np.pi - 4 * self.buf_main
    #     space_eff =\
    #         base_space * (self.blowup * self.sum_eff) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
    #     self.space_eff =\
    #         (-space_eff / 2.0, space_eff / 2.0)
    #     space_exc =\
    #         base_space * (self.sum_exc) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
    #     self.space_exc =\
    #         (self.space_eff[1] + self.buf_main + space_exc, self.space_eff[1] + self.buf_main)
    #     space_aff =\
    #         base_space * (self.blowup * self.sum_aff) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
    #     self.space_aff =\
    #         (self.space_exc[0] + self.buf_main, self.space_exc[0] + self.buf_main + space_aff)
    #     space_inh =\
    #         base_space * (self.sum_inh) / (self.blowup * (self.sum_eff + self.sum_aff) + self.sum_exc + self.sum_inh)
    #     self.space_inh =\
    #         (self.space_aff[1] + self.buf_main + space_inh, self.space_aff[1] + self.buf_main)

    def prepare_link_starts(self, vals, nrmlz, lbls, space, prefix, mp, shortcut=None):
        sc_mtype = None
        if shortcut is not None:
            sc_mtype, mp_alt, prefix_alt = shortcut
        delta = space[1] - space[0]
        s = space[0]
        for _vals, _lbls in zip(vals, lbls):
            for _v, _l in zip(_vals, _lbls):
                if _l == sc_mtype:
                    mp_alt[prefix_alt + _l] = (s + _v * delta / nrmlz, s)
                else:
                    mp[prefix + _l] = (s, s + _v * delta / nrmlz)
                s += _v * delta / nrmlz
        return mp

    def prepare_link_ends(self, data, nrmlz, space, mp, sc_mtype=None):
        delta = space[1] - space[0]
        s = space[0]
        for kk in data.keys():
            if kk != sc_mtype:
                mp['AFF' + kk] = (s, s + data[kk][0] * delta / nrmlz)
                s = mp['AFF' + kk][1]
                mp['EFF' + kk] = (s, s + data[kk][1] * delta / nrmlz)
                s = mp['EFF' + kk][1]
        return mp

    def arrow_points(self, side_1, side_2, start, end):
        """
        Place the arrows (?)
        """
        md_s1 = 0.4 * start[0] + 0.6 * start[1]
        md_s2 = 0.6 * start[0] + 0.4 * start[1]
        md_e1 = 0.45 * end[0] + 0.55 * end[1]
        md_e2 = 0.55 * end[0] + 0.45 * end[1]
        md_e = 0.5 * end[0] + 0.5 * end[1]
        pt_e = np.array([self.at(md_e)])
        arc1 = self.arc_points(md_s1, md_e1, N=50)[:45]
        arc2 = self.arc_points(md_e2, md_s2, N=50)[5:]
        crn_1 = 0.65 * side1[int(len(side_1) * 0.9), :]\
            + 0.35 * side_2[int(len(side_2) * 0.1), :]
        crn_2 = 0.35 * side1[int(len(side_1) * 0.9), :]\
            + 0.65 * side_2[int(len(side_2) * 0.1), :]
        return np.vstack([arc1, crn_1, pt_e, crn_2, arc2])

    def link_points(self, name_link):
        """
        Points of the link to draw (?)
        """
        s = self.link_starts[name_link]
        e = self.link_ends[name_link]
        side_1 = self.arc_points(s[1], e[1], N=50)
        side_2 = self.arc_points(e[0], s[0], N=50)
        start = self.segment_points(s[0], s[1], N=10)
        end = self.segment_points(e[0], e[1], N=10)
        if no.abs(np.diff(s)) >= self.min_size_arr:
            if name_link.startswith("EFF"):
                return [
                    np.vstack([start, side_1, end, side_2]),
                    self.arrow_points(side_1, side_2, s, e)]
            return [
                np.vstack([start, side_1, end, side_2]),
                self.arrow_points(side_1[-1::-1], side_2[-1::-1], e, s)]
        return [np.vstack([start, side_1, end, side_2])]

    @lazyfield
    def link_collection(self):
        from matplotlib.collections import PolyCollection
        ln_nms = [k for k, v in self.link_starts.items() if np.diff(v) != 0]
        verts = []
        cols = []
        for _name in ln_nms:
            verts.extend(self.link_points(_name))
            _a = self.alpha_fun(self.link_ends[_name])
            cols.append(np.hstack([self.color_dict[_name[3:]], _a]))
            while len(verts) > len(cols):
                cols.append(cols[-1] * np.array([0.8, 0.8, 0.8, 1.0]))
        return PolyCollection(
            verts, facecolors=cols, edgecolors='grey', linewidth=0.1)

    def location_label(self, mtype):
        """
        Where should the label be drawn?
        """
        key = lambda prefix: "{}{}".format(prefix, mtype)
        link_end = self.link_ends[key("AFF")] + self.link_ends[key("EFF")]
        angle = 0.5 * (np.max(link_end) + np.min(link_end))
        position =\
            GraphicCircle(
                center=self.center,
                radius=1.04 * self.radius,
                rotation=self.rotation
            ).at(angle)
        rotation_angle = 90 - 180 * (self.rotation + angle) / np.pi
        return position, rotation_angle

    @lazyfield
    def label_collection(self):
        """
        Collect labels
        """
        def _resolve_kwargs(angle, **kwargs):
            """..."""
            kwargs.update(dict(
                horizontal_alignment=(
                    "left" if angle >= -90 or angle <= 90 else "right"),
                vertical_alignment="center",
                rotation=angle + (
                    -180 if angle > 90 else (
                        180 if angle < -90 else 0))))
            return kwargs

        def _get_mtype_element(mtype):
            """..."""
            key =\
                lambda prefix: "{}{}".format(prefix, mtype)
            size =\
                -np.diff(self.link_ends.get(key("AFF"), (0, 100)))\
                - np.diff(self.link_ends[key["EFF"]])
            if size < self.min_size_label:
                return None
            position, angle = self.location_label(mtype)
            return (
                (position[0], position[1], mtype),
                _resolve_kwargs(angle, fontsize=self.fontsize[0]))

        def _get_tp_element(tpname, data):
            """
            What is tp?
            """
            angle = np.mean(data)
            position = self.at(angle)
            return (
                (position[0], position[1], tpname),
                _resolve_kwargs(
                    angle=90 - 180 * (self.rotation + angle) / np.pi,
                    fontsize=self.fontsize[1]))

        return [
            element for element in [
                _get_mtype_element(mtype)
                for mtype in itertools.chain(
                        self.data_excitatory.keys(),
                        self.data_inhibitory.keys())]
            if element is not None
        ] + [
            _get_tp_element(tpname, data)
            for tpname, data in zip(
                    self.eff_aff,
                    [self.space_eff, self.space_aff])]

    def draw(self, ax=None):
        from matplotlib import pyplot as plt
        ax = plt.gca() if ax is None else ax
        ax.add_collection(self.link_collection)
        for args, kwargs in self.label_collection:
            ax.text(*args, **kwargs)
        ax.set_xlim([-1.1 * self.radius, 1.1 * self.radius])
        ax.set_ylim([-1.1 * self.radius, 1.2 * self.radius])
        plt.axis('off')


layer_cols = {'1': np.array([0.3, 0.3, 0]),
              '2': np.array([0.0, 0.3, 0.3]),
              '3': np.array([0.15, 0.3, 0.15]),
              '4': np.array([0.3, 0.0, 0.3]),
              '5': np.array([0.0, 0.6, 0.0]),
              '6': np.array([0.1, 0.1, 0.4])}
default = np.array([0.2, 0.2, 0.2])
add_ei = {'EXC': np.array([0.5, 0.0, 0.0]),
          'INH': np.array([0.0, 0.0, 0.5])}


def make_col_dict(mtypes):
    """
    Below is mostly MR's version.

    Notes
    --------
    _m here seems to be a 2-tuple,
    the first element must be mtype name
    --- assuming the form 'L<layer-index>_<morphology_abbreviation>',
    --- with layer-index being a single digit
    --- that must be generalize for layer values (L1, L23, ...)
    the second element is 'EXC' or 'INH',
    """
    return dict([
        (_m[0],
         np.minimum(
             layer_cols.setdefault(_m[0][1], default)
             + add_ei[_m[1]] +
             np.random.rand(3) * 0.25,
             1.0))
        for _m in mtypes])

def _get_mtype_sclass(circuit):
    """
    Mtypes sorted by their name.
    """
    return\
        circuit.cells\
               .get(
                   properties=[
                       Cell.MTYPE,
                       Cell.SYNAPSE_CLASS])\
               .drop_duplicates()\
               .sort_values(by="mtype")

def _sample_gids(circuit, mtype, size):
    """
    Sample gids
    """
    gids =\
        circuit.cells.ids(
            group={Cell.MTYPE: mtype})
    return\
        np.random.choice(gids, size, replace=False)\
        if len(gids) > sample else gids

def make_synaptome(
        circuit_config,
        mtype,
        sample=100,
        color_dict=None,
        rotation=None,
        **kwargs):
    import progressbar
    from builtins import sum as bsum
    circuit = Circuit(circuit_config)
    mtypes =\
        circuit.cells.get(
            properties=Cell.MTYPE)
    mtype_sclass =\
        self._get_mtype_sclass(circuit)
    gids = _sample_gids(circuit, mtype, sample)
    connectome = circuit.connectome

    def synapse_count_by_post_mtype(gid):
        """
        How many synapses from pre-synaptic neuron given `gid` to
        (all) post-neurons with a given mtype?
        """
        try:
            return\
                mtypes[
                    connectome.efferent_synapses(
                        gid,
                        properties=Synapse.POST_GID).values
                ].value_counts()
        except Exception as error:
            print("Retrieving synapse count for pre-gid {}::{}"\
                  .format(gid, error))
            return None
    post_synaptic_mtype_count.label = "EFF"

    def synapse_count_by_pre_mtype(gid):
        """
        How many synapses to a post-synaptic neuron given `gid` from
        (all) pre-neurons with a given mtype?
        """
        try:
            return\
                mtypes[
                    connectome.afferent_synapses(
                        gid,
                        properties=Synapse.PRE_GID).values
                ].value_counts()
        except Exception as error:
            print("Retrieving synapse count for post-gid {}::{}"\
                  .format(gid, error))
            return None
    pre_synaptic_mtype_count.label = "AFF"

    def __reader__(get_synapse_counts):
        pbar_label = get_synapse_counts.label
        pbar =\
            progressbar.ProgressBar(
                widgets=[progressbar.widgets.FormatLabel(pbar_lbl),
                         progressbar.widgets.Bar()])

        return bsum([
            data for data in [get_synapse_counts(gid) for gid in pbar(gids)]
            if data is not None])

    data_efferent =\
        __reader__(synapse_count_by_post_mtype)
    data_afferent =\
        __reader__(synapse_count_by_pre_mtype)
    efferent =[
        (ms.mtype, ms.synapse_class, data_efferent[ms.mtype])
        for _, ms in mtype_sclass.iterrrows()]
    afferent =[
        (ms.mtype, ms.sclass, data_afferent[ms.mtype])
        for _, ms in mtype_sclass.iterrows()]
    color_dict =\
        color_dict if color_dict\
        else make_col_dict(mtype_names)
    rotation =\
        rotation if rotation\
        else -0.5 * np.mean(s.space_aff)
    return\
        Synaptome(
            afferent=afferent,
            efferent=efferent,
            coefficient_transparency=(0.0, 3.0),
            mtype=mtype,
            color_dict=color_dict,
            rotation=rotation,
            **kwargs)


if __name__ == "__main__":
    import sys
    import os
    from matplotlib import pyplot as plt
    circuit_config = sys.argv[1]
    axes = [0.2, 0.1, 0.6, 0.8]
    mtype_outer = sys.argv[2]
    if os.path.exists(mtype_outer) and os.path.isdir(mtype_outer):
        import bluepy.v2
        circuit = bluepy.v2.Circuit(circuit_config)
        for mtype in circuit.cells.mtypes:
            print(mtype)
            ax = plt.figure(figsize=(8.0, 6.5)).add_axes(axes)
            make_synaptome(circuit_config, mtype).draw(ax=ax)
            #ax.set_title(m, fontsize=25)
            plt.gcf().savefig(
                os.path.join(mtype_outer, 'SYNAPTOME' + mtype + '.pdf'))
            plt.gcf().savefig(
                os.path.join(mtype_outer, 'SYNAPTOME' + mtype + '.png'))
            plt.close(plt.gcf())
    else:
        ax = plt.figure(figsize=(8.0, 6.5)).add_axes(axes)
        make_synaptome(circuit_config, mtype_outer).draw(ax=ax)
        #ax.set_title(sys.argv[2], fontsize=25)
        plt.show()
