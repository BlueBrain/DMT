"""Test reporting for composition."""
import os
from dmt.vtk.utils.collections import Record
from dmt.vtk.author import Author
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.comparison.validation.circuit.composition.by_layer.report\
    import ValidationReport

cr = ValidationReport(
    author = Author.anonymous,
    phenomenon = Phenomenon("fake", "Fake"),
    reference_datasets = {
        'one': Record(
            uri="uri-1",
            short_name = "test-set-1",
            citation = "me, Me, ME - 1",
            what="quoi",
            label="label-1"),
        'two':  Record(
            uri="uri-2",
            short_name = "test-set-2",
            citation = "me, Me, ME - 2",
            what="quoi quoi",
            label="label-2")},
    validation_image_path = "validation/image/path",
    pvalue = 0.01,
    caption = """you should not see anything above""",
    is_pass = True,
    is_fail = False,
    template_location=os.path.join(
        os.path.dirname(__file__),
        "report.cheetah"),
    figure="Fake")

#cr.save(".")
