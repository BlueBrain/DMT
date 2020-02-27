"""
Tools to help analyze.

And essential imports
"""
import os

COUNTERBASE = int(os.environ.get("COUNTERBASE", "100"))
def count_number_calls(LOGGER):
    """decorate..."""
    def decorator(method):
        method.n_calls = 0
        def _decorated(*args, **kwargs):
            result = method(*args, **kwargs)
            method.n_calls += 1
            if method.n_calls % COUNTERBASE == 0:
                LOGGER.info(
                    """{} call count : {}""".format(
                        method.__name__,
                        method.n_calls))
            return result
        return _decorated
    return decorator

from .pathway_measurement import PathwayMeasurement
