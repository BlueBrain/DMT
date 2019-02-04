"""Regression tests --- code that should not break while developing."""

def test_one():
    """Run regression tests"""
    from neuro_dmt.tests.models.bluebrain.circuit.O1.validations.cortex.sscx\
        import composition
    composition.run(
        "rat",
        "composition",
        "cell_density",
        circuit_geometry="F1")

def test_two():
    from neuro_dmt.tests.models.bluebrain.circuit.O1.validations.cortex.sscx\
        import composition
    composition.run(
        "mouse",
        "composition",
        "cell_density",
        circuit_geometry="F1")


def test_all():
    test_one()
    test_two()
