"""Test reporting for composition."""

from dmt.vtk.utils.collections import Record
from dmt.vtk.author import Author
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.validations.circuit.composition.by_layer.validation_report \
    import CompositionReport

cr = CompositionReport(validated_phenomenon = Phenomenon("fake", "Fake"),
                       author = Author.anonymous,
                       validation_datasets = {
                           'one': Record(url="url-1",
                                         short_name = "test-set-1",
                                         citation = "me, Me, ME - 1",
                                         what="quoi"),
                           'two':  Record(url="url-2",
                                         short_name = "test-set-2",
                                         citation = "me, Me, ME - 2",
                                         what="quoi quoi")
                       },
                       validation_image_path = "validation/image/path",
                       p_value = 0.01,
                       caption = """you should not see anything above""",
                       is_pass = True,
                       is_fail = False)

cr.save(".")
