"""Regression tests --- code that should not break while developing."""

def test_one():
    """Test rat SSCx cell density validation for the fake atlas circuit."""
    from neuro_dmt.tests.models.bluebrain.circuit.atlas.validations.cortex.sscx\
        import composition
    composition.run(
        "rat",
        "composition",
        "cell_density",
        circuit_geometry="F1")

def test_two():
    """Test mouse SSCx cell density validation for the fake atlas circuit."""
    from neuro_dmt.tests.models.bluebrain.circuit.atlas.validations.cortex.sscx\
        import composition
    composition.run(
        "mouse",
        "composition",
        "cell_density",
        circuit_geometry="F1")

def test_three():
    """Test rat SSCx cell density validation for the (real) atlas circuit."""
    from neuro_dmt.tests.models.bluebrain.circuit.atlas.validations.cortex.sscx\
        import composition
    composition.run(
        "rat",
        "composition",
        "cell_density",
        circuit_geometry="S1")

def test_all():
    test_one()
    test_two()
