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

    
def use(head, *tail):	
    """
    Decorate a method with terms used in its body.
    """
    terms = (head,) + tail

    def decorator(method):	
        sig = inspect.signature(method)	
        sigparams = sig.parameters
        missing_params = [p for p in terms if p not in sigparams]	

        signature_has_varkwargs = any(
            p.kind == p.VAR_KEYWORD for p in sigparams.values())

        def check_varkwargs(kwargs):
            """check that kwargs does not contain unknown arguments."""
            for param in kwargs:
                if not param in sigparams and not param in terms:
                    raise TypeError(
                        "{} got an unexpected keyword argument {}".format(
                            method, param))

        if any(missing_params) and not signature_has_varkwargs:	
            raise TypeError(	
                "parameters: {} are not found in the signature"	
                "{} of function {}".format(	
                    missing_params, sig, method))	

        @functools.wraps(method)	
        def wrapped_method(*args, **kwargs):	
            """
            The decorated method.
            """
            if signature_has_varkwargs:
                check_varkwargs(kwargs)
            return method(*args, **kwargs)	

        docstring = wrapped_method.__doc__	
        if docstring is None:	
            docstring = ""	

        if "{parameters}" not in docstring:	
            docstring = docstring + "Parameters:\n    {parameters}"	

        params_posn = docstring.find("{parameters}")	
        preceding_newline = docstring[:params_posn].rfind("\n") + 1	
        leading_whitespace = " " * (params_posn - preceding_newline)	
        wrapped_method.__doc__ = docstring.format(	
            parameters=("\n" + leading_whitespace)	
            .join(p.document for p in terms))	
        return wrapped_method	

    return decorator
