"""
Test, and develop `BrainCircuitAnalysis`
"""
from pathlib import Path
import pytest as pyt
import pandas as pd
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting.bars import Bars
from dmt.tk.parameters import Parameters
from dmt.tk.reporting import Report, Reporter
from neuro_dmt.models.bluebrain.circuit.test import mock
from dmt.analysis import Suite as AnalysisSuite
from dmt.tk.parameters import Parameters
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils import get_label
from ..composition.interfaces import CellDensityAdapterInterface
from .. import BrainCircuitAnalysis

def test_adapter_resolution():
    """
    `BrainCircuitAnalysis` should be able to resolve which adapter to use.
    """
    cell_density_phenomenon =\
        Phenomenon(
            "Cell Density",
            "Count of cells in a unit volume.",
            group="composition")
    model = mock.get_circuit_model()
    adapter = mock.get_circuit_adapter(model)
    analysis =\
        BrainCircuitAnalysis(
            phenomenon=cell_density_phenomenon,
            AdapterInterface=CellDensityAdapterInterface,
            measurement_parameters=Parameters(
                pd.DataFrame({"layer": range(1, 7)})),
            plotter=Bars(
                xvar="layer",
                xlabel="Layer",
                yvar=cell_density_phenomenon.label,
                ylabel=cell_density_phenomenon.name,
                gvar="dataset"))

    with pyt.raises(TypeError):
        analysis(model)

    with pyt.raises(TypeError):
        analysis._resolve_adapter_and_model(model)

    analysis.adapter = adapter

    assert analysis._resolve_adapter_and_model(model)\
        == (adapter, model)

    assert analysis._resolve_adapter_and_model(model, adapter)\
        == (adapter, model)

    for a, m in 10 * [(adapter, model)]:
        assert analysis._resolve_adapter_and_model(model) == (a, m)

def path_gpfs_project(number, *args):
    """
    Path to the project, given its number
    """
    return Path("/gpfs/bbp.cscs.ch/project/")\
        .joinpath("proj{}".format(number))\
        .joinpath(*args)


class CircuitAnalysisTest(WithFields):
    """
    Construct and test a cell density analysis
    """
    analysis = Field(
        """
        The circuit model analysis to test.
        This class assumes that a reporter was not set for this analysis.
        """)

    def test_get_measurement(self, *args, **kwargs):
        """
        Measurement returned by an analysis should be a pandas data-frame.
        """
        datasets =\
            self.analysis._with_reference_data(
                self.analysis.get_measurement(*args))
        for dataset in datasets.values():
            assert isinstance(dataset, pd.DataFrame)
        expected_datasets = kwargs.get("expected_datasets", [])
        for label in expected_datasets:
            assert label in datasets,\
                "Expected dataset {} not in {}".format(
                    label,
                    datasets)
        return datasets

    def test_get_report(self, *args):
        """
        Report generated by analysis should have figures.
        """
        report = self.analysis.get_report(*args)
        assert isinstance(report, Report)
        assert len(report.figures) > 0
        assert hasattr(report, "measurement")
        return report

    def test_call_analysis(self, *args):
        """
        The analysis should be a callable, and return a report when called.
        """
        report = self.analysis(*args)
        assert isinstance(report, Report)

    def test_post_report(self, *args, **kwargs):
        """
        The reporter should place the report in a folder.
        """
        phenomenon = get_label(self.analysis.phenomenon)
        report = self.analysis(*args, **kwargs)
        output_path =\
            Path.cwd().joinpath(
                kwargs.get("output_folder", ""))
        reporter =\
            Reporter(path_output_folder=output_path)
        path_report =\
            Path(reporter.post(report))
        assert path_report == output_path.joinpath(get_label(phenomenon)),\
            "{} != {}".format(
                path_report,
                output_pat.joinpath(get_label(phenomenon)))
        assert path_report.is_dir()
        assert any(p.is_file() for p in path_report.glob("report*")),\
            "Did not find a report file."
        path_report_figures = path_report.joinpath("figures")
        assert path_report_figures.is_dir()

        for name_figure in report.figures:
            path_figure = path_report_figures\
                .joinpath("{}.png".format(name_figure))
            assert path_figure.is_file()

        name_measurement = "{}.csv".format(phenomenon)
        path_measurement = path_report.joinpath(name_measurement)
        assert path_measurement.is_file(),\
            "Analysis did not save a measurement {}.".format(name_measurement)
        measurement = pd.read_csv(path_measurement, header=0)
        for p in self.analysis.names_measurement_parameters:
            assert p in measurement.columns,\
                "Saved measurement did not have a column for parameter {}"\
                .format(p)
        assert phenomenon in measurement.columns,\
            "Saved measurement did not have a column for the phenomenon"

    @classmethod
    def suite(cls, adapter):
        """
        A suit of analyses.
        """
        cell_density_phenomenon =\
            Phenomenon(
                "Cell Density",
                "Count of cells in a unit volume",
                group="Composition")
        return AnalysisSuite(*(
            BrainCircuitAnalysis(
                phenomenon=phenomenon,
                AdapterInterface=AdapterInterface,
                measurement_parameters=Parameters(
                    pd.DataFrame({"layer": range(1,7)})),
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="dataset"),
                adapter=adapter)
            for phenomenon, AdapterInterface in (
                    (cell_density_phenomenon, CellDensityAdapterInterface),)))
