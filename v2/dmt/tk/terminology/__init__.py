"""
Use an established terminology in method calls.
"""
import inspect	
import functools	


class Term(str):	
    """	
    Terms are used in an analysis as query parameters, or dataframe column
    names. As a subclass of `str` `class Term` can act as such a label,
    while encapsulating the description of that term.

    Intended Usage
    -----------------
    1. As parameters to a query: Parameters are provided to functions to e.g. 
    get a measurement commonly used parameters will have a name and a .	
    description for all intents and purposes they are a string, s.t. they can	
    be passed with **kwargs	
    """	
    def __new__(cls, term, *args):	
        """
        Arguments
        ----------
        `term`: single word label.
        """
        return super().__new__(cls, term)	

    def __init__(self, term, description):	
        """
        Arguments
        ------------
        `term`: single word label
        `description`: description of the term
        """
        self.description = description
        return super().__init__()	

    @property
    def document(self):	
        return "{}: {}" .format(self, self.description)


class MissingParameterException(TypeError):	
    pass	


def _check_missing_in_signature(expected, method):
    """
    Check that the method accepts expected parameters.

    Arguments
    `expected`: Expected terms
    """
    signature = inspect.signature(method)
    missing_params = [
        term for term in expected
        if term not in signature.parameters]
    signature_has_varkwargs = any(
        p.kind == p.VAR_KEYWORD
        for p in signature.parameters.values())
    if any(missing_params) and not signature_has_varkwargs:
        raise TypeError(
            "parameters: {} are not found in the signature"	
            "{} of function {}".format(	
                missing_params, signature, method.__name__))

    return True
    
def _check_varkwargs(
        expected_params,
        method,
        varkwargs):
    """
    Check that method kwargs does not contain unknown arguments.
    """
    for param in varkwargs:
        if not param in expected_params:
            raise TypeError(
                "{} got an unexpected keyword argument {}".format(
                    method, param))

    return True

def use(head, *tail):	
    """
    Decorate a method with terms used in its body.
    """
    terms = (head,) + tail

    def decorator(method):	
        signature = inspect.signature(method)	

        signature_has_varargs = any(
            p.kind == p.VAR_POSITIONAL for p in signature.parameters.values())
        signature_has_varkwargs = any(
            p.kind == p.VAR_KEYWORD for p in signature.parameters.values())

        _check_missing_in_signature(terms, method)

        @functools.wraps(method)	
        def wrapped_method(*args, **kwargs):	
            """
            The decorated method.
            """
            if signature_has_varkwargs:
                _check_varkwargs(
                    terms + tuple(p for p in signature.parameters),
                    method, kwargs)
            try:
                return method(*args, **kwargs)
            except KeyError as key_error:
                if key_error[0] in terms:
                    raise TypeError(
                        "Missing keyword argument {}".format(key_error[0]))
                raise key_error

        docstring = wrapped_method.__doc__	
        if docstring is None:	
            docstring = ""	

        if "{parameters}" in docstring:
            arguments_label = "parameters"
        elif "{arguments}" in docstring:
            arguments_label = "arguments"
        else:
            docstring = docstring + "Arguments:\n    {arguments}"
            arguments_label = "arguments"

        params_posn = docstring.find("{" + arguments_label + "}")
        preceding_newline = docstring[:params_posn].rfind("\n") + 1	
        leading_whitespace = "\n" + " " * (params_posn - preceding_newline)	
        wrapped_method.__doc__ = docstring.format(**{
            arguments_label: leading_whitespace.join(
                term.document for term in terms)})
            
        return wrapped_method	

    return decorator


