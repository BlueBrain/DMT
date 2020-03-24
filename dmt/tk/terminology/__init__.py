"""
Use an established terminology in method calls.
"""
import inspect	
import functools	


class MissingTermError(TypeError):
    pass


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

    def document(self, label=None):	
        if label is None:
            label = self
        return "{}: {}" .format(label, self.description)


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
        raise MissingTermError(
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
            raise MissingTermError(
                "{} got an unexpected keyword argument {}".format(
                    method, param))

    return True

def _terms_decorated_doc_string(terms, docstring):
    """
    Add term-arguments to the doc string.
    """
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
    try:
        return docstring.format(**{
            arguments_label: leading_whitespace.join(
                term.document(label) for label, term in terms.items())})
    except AttributeError:
        return docstring.format(**{
            arguments_label: leading_whitespace.join(
                term.document() for term in terms)})

def _match_kwargs(**term_dict):
    """
    Decorate a method to match keyword arguments to those declared in the
    decoration.
    """
    def decorator(method):
        """
        Decorate a method
        """
        signature = inspect.signature(method)
        signature_has_varkwargs = any(
            p.kind == p.VAR_KEYWORD for p in signature.parameters.values())

        assert len(signature.parameters) == 1 and signature_has_varkwargs,\
            "_match_kwargs applies only to methods that accept only var-kwargs"

        @functools.wraps(method)	
        def wrapped_method(**kwargs):
            """
            The decorated method.
            """
            for p in term_dict.values():
                if p not in kwargs:
                    raise MissingTermError(
                        "Missing required keyword argument {}".format(p))

            return method(**{
                label: kwargs.get("{}".format(term))
                for label, term in term_dict.items()}) 

        wrapped_method.__name__ = method.__name__
        wrapped_method.__doc__ = _terms_decorated_doc_string(
            term_dict,
            method.__doc__)
        return wrapped_method

    return decorator

def _require_if(head, *tail, with_required_kwargs=True):	
    """
    Decorate a method with terms used in its body,
    requiring keywords if `with_required_kwargs`.
    """
    terms = (head,) + tail

    def decorator(method):
        """
        Decorate a method
        """
        if with_required_kwargs:
            try:
                return _match_kwargs(**{
                    "{}".format(term): term
                    for term in terms})(method)
            except AssertionError:
                pass

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
                if key_error.args[0] in terms:
                    raise KeyError(
                        "{}; are you sure you provided {} in {}?"
                        .format(key_error, key_error.args[0], method.__name__))
                raise key_error

        wrapped_method.__name__ = method.__name__
        wrapped_method.__doc__ = _terms_decorated_doc_string(
            terms,
            method.__doc__)

        return wrapped_method

    return decorator

def require(head, *tail):
    """
    Always require keyword
    """
    return _require_if(head, *tail, with_required_kwargs=True)

def use(head, *tail):
    """
    Decorate a method with terms used in its body.
    """
    return _require_if(head, *tail, with_required_kwargs=False)

def where(**term_dict):
    """
    Declare what a method means by the terms it uses in its argument list.
    """
    def decorator(method):
        """
        Decorate a method
        """
        try:
            return _match_kwargs(**term_dict)(method)
        except AssertionError:
            pass

        signature = inspect.signature(method)
        signature_has_varargs = any(
            p.kind == p.VAR_POSITIONAL for p in signature.parameters.values())
        signature_has_varkwargs = any(
            p.kind == p.VAR_KEYWORD for p in signature.parameters.values())
        if signature_has_varkwargs or signature_has_varargs:
            raise TypeError(
                "terminology.where does not support var-args or var-kwargs")

        @functools.wraps(method)
        def wrapped_method(*args, **kwargs):
            """
            The decorated method.
            """
            return method(*args, **kwargs)
            # return method(**{
            #     label: kwargs.get("{}".format(term))
            #     for label, term in term_dict.items()})

        wrapped_method.__name__ = method.__name__
        wrapped_method.__doc__ = _terms_decorated_doc_string(
            term_dict,
            method.__doc__)
        return wrapped_method

    return decorator



from .collection import TermCollection
