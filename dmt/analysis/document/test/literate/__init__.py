"""
Test develop
Documented analysis written using classes.
"""
from abc import ABCMeta
from ...report import LabReport
from ..import get_path_save

class LiterateMeta(ABCMeta):
    """
    Literate programming to write analyses.
    Construct classes that also document their doc-strings as
    as scientific paper.

    Python doc-strings are the key!

    In literate programming the computer program is given an explanation of its
    logic in a natural language, interspersed with snippets of macros and
    traditional source code, from which compatible source code can be generated.
    Literate programs are written as an uninterrupted exposition of logic in an
    ordinary human language, much like the text of an essay, in which macros
    are included to hide abstractions and traditional source code.
    Treat a program as a piece of literature, addressed to human beings rather
    than to a computer.
    As a hypertext document.

    Literate programming focuses on programming itself.
    We will use the process of literate programming to develop tools and
    convention to write a scientific-paper directly in Python.
    Indeed, a human readable document is produced by Jupyter notebooks ---
    but the notebook format does not allow to extract the code in the
    notebook as a single module. Out scientific-literate-programming manuscripts
    are intended as single source of information on a topic for both the
    computer and the human. The computer can use the information in the
    manuscript to run a simulation and do data and scientific analysis.
    The human can use the information to understand and further develop the
    scientific concept developed in the manuscript.

    For example, we can have the manuscript produce a scientific paper for the
    human and a module of code for the computer.
    """
 
class DocumentedLabReport:
    """
    Base class to weave documentation into a python class definition.
    The analyst can compose a Python class as a documented analysis.
    """
    def __new__(cls, ):
        """
        TODO:
        1. 
        """


class LayerThickness(DocumentedLabReport):
    """
    Total cortical, and relative layer thicknesses are analyzed.
    """
    pass
