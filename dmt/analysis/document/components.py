# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Components of a documented analysis.
"""
from pickle import PicklingError
import json
from dmt.tk.field.exceptions import MissingFieldError
from ..measurement import\
    Measurement, MeasurementSuite,\
    CompositeData, save_elemental
from .import *


class Section(DocElem):
    @field.cast(Narrative)
    def narrative(self):
        """
        A text that will become the story told in this section.
        """
        raise FieldIsRequired

    def __init__(self, *args, **kwargs):
        """...
        """
        try:
            super().__init__(*args, **kwargs)
        except MissingFieldError as missing_field_error:
            try:
                super().__init__(*args[1:], **args[0], **kwargs)
            except IndexError:
                raise missing_field_error
            except TypeError:
                super().__init__(narrative=args[0], *args[1:], **kwargs)

    @field.cast(Data)
    def data(self):
        """
        Data for this section.
        """
        return NA

    @field.cast(CompositeData)
    def tables(self):
        """
        A collection of dataframes or paths to dataframes.
        """
        return NA

    @field.cast(CompositeIllustration)
    def illustration(self):
        """
        Illustration for this section.
        """
        return NA

    def save(self, section, path_folder):
        """..."""
        path_section = path_folder.joinpath(section.label)
        path_section.mkdir(parents=False, exist_ok=True)
        try:
            narrative = section.narrative
        except AttributeError:
            narrative = None
        try:
            data = section.data
        except AttributeError:
            data = None
        try:
            tables = section.tables
        except AttributeError:
            tables = None
        try:
            illustration = section.illustration
        except AttributeError:
            illustration = None

        record = Record(_=path_section)
        if narrative:
            record = record.assign(
                narrative=self.narrative.save(
                    narrative, path_section))
        if data:
            record = record.assign(
                data=self.data.save(
                    data, path_section))
        if tables:
            record = record.assign(
                tables=tables.save(
                    path_section, "tables"))
        if illustration:
            record = record.assign(
                illustration=self.illustration.save(
                    illustration, path_section))

        for subsection in self.children:
            record = record.assign(**{
                subsection.label: subsection.save(
                    section.children, path_section)})

        return record

    def get_illustration_data(self, adapter, model, *args, **kwargs):
        """
        Data for illustrations.

        Override this ....
        """
        return self.data(adapter, model, *args, **kwargs)

    def get_tables_values(self, adapter, model, *args, **kwargs):
        """..."""
        def _evaluate(label, table):
            if callable(table):
                measurement = self.measurements[label]
                return table(measurement(adapter, model, *args, **kwargs))
            else:
                return table

        return CompositeData(OrderedDict([
            (label, _evaluate(label, table))
            for label, table in self.tables.items()
        ]))

    def _latex_illustration(self, section, path_tree_report):
        """
        Generate latex code for illustrations.

        TODO:
        This method can be moved to `CompositeIllustration`!
        """
        path_section = getattr(path_tree_report, self.label)
        try:
            illustration = section.illustration
        except AttributeError:
            return ""
        try:
            path_illustration = path_section.illustration
        except AttributeError:
            return ""

        latex = ""
        for label, figures in path_illustration.items():
            caption = illustration[label].caption
            figure_tex ="""
            \\begin{figure}[hbt!]
            """.strip()
            if isinstance(figures, Mapping):
                if len(figures) == 1:
                    figure_tex += """
                    \\includegraphics[width=1.00\\textwidth]{fig-location}
                    """.strip()\
                      .replace("fig-location",
                                str(list(figures.values())[0]))
                else:
                    for sub_label, sub_figure_path in figures.items():
                        sub_figure_tex = """
                        \\subfloat[fig-label]{\\includegraphics[width=0.65\\textwidth]{fig-location}}
                        """.strip()\
                          .replace("fig-label",
                                    "{}".format(sub_label))\
                          .replace("fig-location",
                                    str(sub_figure_path.relative_to(path_tree_report._)))
                        figure_tex += "\n" + sub_figure_tex + "\\\\\n" + "\\\\\n"
            else:
                figure_tex += """
                \\includegraphics[width=1.00\\textwidth]{fig-location}
                """.strip()\
                  .replace("fig-location",
                            str(figures.relative_to(path_tree_report._)))

            figure_tex += "\\caption{figure-caption}\n".replace("figure-caption",
                                                                caption)
            figure_tex += "\\end{figure}\n"

            latex += "\n" + figure_tex
        return latex

    def _latex_tables(self, section, path_tree_report):
        """
        Generate latex code for tables.

        TODO:
        This method can be moved to `CompositeData`!
        """
        path_section = getattr(path_tree_report, self.label)
        try:
            tables = section.tables
        except AttributeError:
            return ""
        try:
            path_tables = path_section.tables
        except AttributeError:
            return ""

        latex = ""
        for label, table in tables.items():
            latex += "{\\bf label}\\\\\n".replace("label",
                                                  ' '.join(w.capitalize()
                                                           for w in label.split('_')))
            latex += "\n" + table.to_latex(index=False)
            latex += "\\\\\n\\\\"

        return latex

    def to_latex(self, section, path_tree_report):
        """
        Assemble a latex for section.
        """
        path_section = getattr(path_tree_report, self.label)
        latex = section.narrative
        latex += self._latex_illustration(section, path_tree_report)
        latex += self._latex_tables(section, path_tree_report)
        return latex


    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return Record(
            title=self.title,
            label=self.label,
            narrative=self.narrative(
                adapter, model, *args, **kwargs),
            data=self.data(
                adapter, model, **kwargs),
            tables=self.get_tables_values(
                adapter, model, *args, **kwargs),
            illustration=self.illustration(
                adapter, model, *args,
                data=self.get_illustration_data(
                    adapter, model, **kwargs),
                **kwargs))


class Abstract(DocElem):
    """ Abstract to an argument, is a `DocElem` but not a section. """
    title = "Abstract"
    label = "abstract"
    @field.cast(Narrative)
    def narrative(self):
        """
        A text that will become the story told in this section.
        """
        raise FieldIsRequired

    def __init__0(self, narrative=None, *args, **kwargs):
        """
        Initialize `Abstract` with a story.
        """
        if not narrative:
            raise TypeError(
                "{} needs a narrative".format(
                    self.__class__.__name__))
        super().__init__(*args, narrative=narrative, **kwargs)

    def __init__(self, *args, **kwargs):
        """...
        """
        try:
            super().__init__(*args, **kwargs)
        except MissingFieldError as missing_field_error:
            try:
                super().__init__(*args[1:], **args[0], **kwargs)
            except IndexError:
                raise missing_field_error
            except TypeError:
                super().__init__(narrative=args[0], *args[1:], **kwargs)


    def save(self, abstract, path_folder):
        """
        Save an abstract value computed for some adapter, model.
        """
        path_abstract = path_folder.joinpath("abstract")
        path_abstract.mkdir(parents=False, exist_ok=True)
        return self.narrative.save(abstract.narrative, path_abstract)

    def to_latex(self, abstract, path_abstract):
        """
        Arguments
        --------------
        path_abstract :: object returned by `Abstract.save`
        """
        return abstract.narrative

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return Record(
            title=self.title,
            label=self.label,
            narrative=self.narrative(adapter, model, *args, **kwargs))


class Introduction(Section):
    """
    Make Section an Introduction
    """
    title = "Introduction"


class Methods(Section):
    """..."""
    title = "Methods"
    @field.cast(MeasurementSuite)
    def measurements(self):
        """
        A dict that will be cast to become a `MeasurementSuite`.
        """
        return NA

    @field.cast(CompositeData)
    def reference_data(self):
        """
        Reference data to be used for analysis.

        Valid values
        ---------------
        1.`pandas.DataFrame`
        2. Mapping{label -> pandas.DataFrame}

        Examples
        ---------------
        { "cell_density": {label_x: data_x, label_y: data_y} }
        """
        return NA

    def save(self, value, path_folder):
        """
        Save a value of this methods instance evaluated for a given
        adapter, model
        """
        path_methods = super().save(value, path_folder)
        try:
            measurements = value.measurements
        except AttributeError:
            measurements = None
        if measurements:
            path_measurements = path_methods._.joinpath("measurements.json")
            with open(path_measurements, 'w') as f:
                json.dump(measurements, f)
            path_methods.assign(measurements=path_measurements)
        try:
            reference_data = value.reference_data
        except AttributeError:
            reference_data = None
        if reference_data is not None:
            path_methods.assign(
                reference_data=reference_data.save(
                    path_methods._, "reference_data"))
        return path_methods

    def to_latex(self, methods, path_artefacts):
        latex = methods.narrative

        try:
            measurements_methods = methods.measurements
        except AttributeError:
            measurement_methods = {}
        if measurements_methods:
            latex += "Folowing measurements were made on the model:\n"
            latex += "\\begin{itemize}\n"
            for label, description in measurements_methods.items():
                latex += "\\item {\\bf label}: description\n".replace(
                    "label", ' '.join(w.capitalize() for w in label.split('_'))
                ).replace(
                    "description", description.strip())
            latex += "\\end{itemize}\n"

        return latex

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return\
            super().__call__(
                adapter, model, *args, **kwargs
            ).assign(
                reference_data=self.reference_data,
                measurements=OrderedDict([
                    (l, m.description(adapter, model, *args, **kwargs))
                    for l, m in self.measurements.items()]))


class Results(Section):
    title = "Results"

    @lazyfield
    def measurements(self):
        return self.parent.methods.measurements

    @lazyfield
    def reference_data(self):
        return self.parent.methods.reference_data

    def get_illustration_data(self, adapter, model, *args, **kwargs):
        """
        Gather measurement and reference data.
        """

        def _get_data(dataset):
            try:
                return dataset.data
            except AttributeError:
                return dataset

        data_illustration = OrderedDict()

        measurements = self.measurements(adapter, model, *args, **kwargs)

        def _align(reference_data, measurement_data):
            """
            Align reference data to the measurement.
            """
            try:
                return reference_data.set_index(measurement_data.index.names)
            except KeyError:
                if reference_data.index.names != measurement_data.index.names:
                    raise ValueError(
                        """
                        Measurement and Reference data do not have the same indices:
                        \t Reference index names: {}.
                        \t Measurement index names {}
                        """.format(reference_data.index.names,
                                   measurement_data.index.names))
                return reference_data


        for label_measurement, data_measurement in measurements.items():
            reference_data =\
                self.reference_data.get(label_measurement, NA)
            data_illustration[label_measurement] ={
                adapter.get_label(model): data_measurement}
            if reference_data is not NA:
                if not isinstance(reference_data, Mapping):
                    reference_data = {"reference": _align(reference_data,
                                                          data_measurement)}
                data_illustration[label_measurement].update({
                    label: _align(_get_data(data),
                                  data_measurement)
                    for label, data in reference_data.items()})

        for label_data, reference_data in self.reference_data.items():
            if label_data not in data_illustration:
                data_illustration[label_data] = reference_data

        return data_illustration

    def save(self, value, path_folder):
        """
        Save a value of this results instance evaluated for a given
        adapter, model
        """
        path_results = super().save(value, path_folder)
        try:
            measurements = value.measurements
        except AttributeError:
            measurements = None
        if measurements:
            try:
                path_measurements =\
                    measurements.save(path_results._, "measurements")
            except AttributeError:
                path_measurements =\
                    save_elemental(measurements, "measurement", path_folder)
            path_results =\
                path_results.assign(measurements=path_measurements)
        return path_results


    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        return\
            super().__call__(
                adapter, model, *args, **kwargs
            ).assign(
                reference_data=self.reference_data,
                measurements=self.measurements(adapter, model, **kwargs))


class Discussion(Section):
    title = "Discussion"
    pass


class Conclusion(Section):
    title = "Conclusion"
    pass
