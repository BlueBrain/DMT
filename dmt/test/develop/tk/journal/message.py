"""
Test develop journal.Message
"""

from dmt.v2.tk.journal.message import *

def test_addition():
    """
    Messages should be addable.
    """
    suggestion =\
        Suggestion(
            "You should revise implementation of Message if this test fails")
    additional_suggestion =\
        Suggestion(
            "And move onto something else if the test passes")
    total_suggestion =\
        suggestion + additional_suggestion
    total_suggestion_strs =\
        total_suggestion._value.split('\n')

    assert len(total_suggestion_strs) == 2,\
        "Additional message should be added as new lines."
    assert total_suggestion_strs[0] == suggestion._value,\
        "Additional message should be added as new lines."
    assert total_suggestion_strs[1] == additional_suggestion._value,\
        "Additional message should be added as new lines."



