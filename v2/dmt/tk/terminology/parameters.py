import inspect
import functools


class Parameter(str):
    """
    parameters are provided to functions to e.g. get a measurement
    commonly used parameters will have a name and a description.
    for all intents and purposes they are a string, s.t. they can
    be passed with **kwargs
    """
    def __new__(cls, param_keyword, description):
        return super().__new__(cls, param_keyword)

    def __init__(self, param_keyword, description):
        self.description = description
        return super().__init__()

    def document(self):
        return ": ".join([self, self.description])


class MissingParameterException(TypeError):
    pass


def with_parameters(*params):

    def decorator(method):
        sig = inspect.signature(method)
        sigparams = sig.parameters
        missing_params = [p for p in params if p not in sigparams]

        def has_varkwargs(sigparams):
            """test for **kwargs-style argument"""
            return any(p.kind == p.VAR_KEYWORD for p in sigparams.values())

        if any(missing_params) and not has_varkwargs(sigparams):
            raise MissingParameterException(
                "parameters: {} are not found in the signature"
                "{} of function {}".format(
                    missing_params, sig, method))

        @functools.wraps(method)
        def wrapped_method(*args, **kwargs):
            return method(*args, **kwargs)

        docstring = wrapped_method.__doc__
        params_posn = docstring.find("{parameters}")
        preceding_newline = docstring[:params_posn].rfind("\n") + 1
        leading_whitespace = " " * (params_posn - preceding_newline)
        wrapped_method.__doc__ = docstring.format(
            parameters=("\n" + leading_whitespace)
            .join(p.document() for p in params))
        return wrapped_method

    return decorator
