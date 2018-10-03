"""Test develop ParameterGroup"""
from dmt.vtk.measurement.parameter.group import ParameterGroup
from dmt.tests import ExceptionalTest
from dmt.vtk.utils.logging import Logger
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.parameters import NamedTarget

logger = Logger(__name__, level=Logger.level.TEST)

def test_one_param():
    """Test labels for ParameterGroup of one parameter"""
    pset = {CorticalLayer()}
    pg = ParameterGroup(*list(pset))
    logger.info(logger.get_source_info(),
                "Parameter group with two parameters has label {}"\
                .format(pg.label))
    expected = "layer"
    if pg.label != expected:
        raise ExceptionalTest.Failure("{} != {}".format(pg.label, expected))

    return ExceptionalTest.Success(test_one_param.__doc__)
    
ExceptionalTest(test_one_param, source_info=logger.get_source_info()).run()

def test_two_param():
    """Test labels for ParameterGroup of two parameters"""
    pset = {CorticalLayer(), NamedTarget()}
    pg = ParameterGroup(*list(pset))
    logger.info(logger.get_source_info(),
                "Parameter group with two parameters has label {}"\
                .format(pg.label))
    expected = "$target_layer"
    if pg.label != expected:
        raise ExceptionalTest.Failure("{} != {}".format(pg.label, expected))

    return ExceptionalTest.Success(test_two_param.__doc__)

ExceptionalTest(test_two_param, source_info=logger.get_source_info()).run()
