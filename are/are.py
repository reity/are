"""Abstract regular expressions.

Library for working with regular expressions as abstract
mathematical objects.
"""

from __future__ import annotations
import doctest
from collections.abc import Iterable
from itertools import chain

class are(tuple):
    """
    Base class for abstract regular expression instances
    (and nodes of the tree data structure that represents
    abstract regular expression instances).
    """

class emp(are):
    """
    Regular expression that only matches an empty
    string (i.e., a string with length zero).

    >>> emp()(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    >>> (emp()(""), emp()("ab"))
    (0, None)
    >>> emp()("abc", full=False)
    0
    """
    def __new__(cls):
        return super().__new__(cls)

    def __call__(self, string, full=True, _string=None, _success=None):
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string
        _success = {} if _success is None else _success

        try:
            symbol = next(string)
            _string[()] = chain([symbol], string) # Restore symbol to string.

            if not full:
                _success[()] = chain([symbol], string)
                return 0
            else:
                _success[()] = None
                return None

        except StopIteration:
            _string[()] = string
            _success[()] = string
            return 0

class lit(are):
    """
    Literal node (individual symbol as a base case) of a regular
    expression instance.

    >>> (lit("a")(""), lit("a")("a"), lit("a")("ab"))
    (None, 1, None)
    >>> (lit("a")("", full=False), lit("a")("ab", full=False))
    (None, 1)
    >>> lit("a")(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string, full=True, _string=None, _success=None):
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string
        _success = {} if _success is None else _success

        try:
            symbol = next(string)

            if symbol == self[0]:
                _string[()] = chain([symbol], string) # Restore symbol to string.

                if not full:
                    _success[()] = string
                    return 1
                else:
                    _string_ = {}
                    result = emp()(string, full=True, _string=_string_)
                    if result == 0:
                        _success[()] = string
                        return 1
                    string = _string_[()] # Restore string if above attempt failed.

            _string[()] = chain([symbol], string) # Restore symbol to string.
            _success[()] = None
            return None # String does not satisfy the regular expression.

        except StopIteration:
            _string[()] = string
            _success[()] = None
            return None

class con(are):
    """
    Concatenation operation node for two regular expressions.

    >>> r = con(lit('a'), lit('b'))
    >>> (r('ab'), r('a'), r('abc'), r('cd'))
    (2, None, None, None)
    >>> (r('a', full=False), r('abc', full=False), r('cd', full=False))
    (None, 2, None)
    >>> r = con(lit('a'), con(lit('b'), lit('c')))
    >>> (r('abc'), r('abcd', full=False), r('ab'))
    (3, 3, None)
    >>> r = con(con(lit('a'), lit('b')), lit('c'))
    >>> r('abc')
    3
    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, string, full=True, _string=None, _success=None):
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string
        _success = {} if _success is None else _success

        lengths = self[0](string, full=False, _string=_string, _success=_success)
        if lengths is not None:
            string = _success[()]
            _string_ = {}
            _success_ = {}
            length = self[1](string, full=False, _string=_string_, _success=_success_)
            if length is not None:
                string = _success_[()]
                lengths += length

                if not full:
                    _success[()] = string
                    return lengths
                else:
                    _string__ = {}
                    result = emp()(string, full=True, _string=_string__)
                    if result == 0:
                        _success[()] = string
                        return lengths
                    string = chain(_string__[()], string) # Restore string if above check failed.

            # Restore consumed symbols to string and fail.
            _string[()] = chain(_string[()], chain(_string_[()], string))
            _success[()] = None
            return None # String does not satisfy the regular expression.

        # Restore consumed symbols to string and fail.
        _string[()] = chain(_string[()], string)
        _success[()] = None
        return None # String does not satisfy the regular expression.

class alt(are):
    """
    Alternation operation node for two regular expressions.

    >>> r = alt(con(lit('a'), lit('b')), lit('a'))
    >>> r('abc', full=False)
    2
    >>> r = alt(lit('a'), con(lit('a'), lit('a')))
    >>> r('aaa', full=False)
    2
    >>> r = alt(lit('a'), con(lit('a'), lit('a')))
    >>> r('aaa') is None
    True
    >>> r = alt(con(lit('a'), lit('a')), lit('a'))
    >>> r('aa', full=False)
    2
    >>> r = alt(lit('a'), lit('a'))
    >>> r('a')
    1
    >>> r = alt(lit('a'), lit('b'))
    >>> r('ac') is None
    True
    >>> (r('a'), r('b'), r('c'))
    (1, 1, None)
    >>> r('ac', full=False)
    1
    >>> r = con(alt(lit('a'), lit('b')), lit('c'))
    >>> (r('ac'), r('bc'), r('c'), r('a'), r('b'))
    (2, 2, None, None, None)
    >>> r = con(alt(lit('a'), lit('b')), alt(lit('c'), lit('d')))
    >>> (r('ac'), r('ad'), r('bc'), r('bd'))
    (2, 2, 2, 2)
    >>> r0 = alt(lit('a'), alt(lit('b'), lit('c')))
    >>> r1 = con(r0, r0)
    >>> {r1(x + y) for x in 'abc' for y in 'abc'}
    {2}
    >>> r = alt(con(lit('a'), lit('a')), lit('a'))
    >>> r('aa')
    2
    >>> r = alt(lit('b'), con(lit('a'), lit('a')))
    >>> r('aa')
    2
    >>> r = alt(lit('b'), con(lit('c'), lit('a')))
    >>> r('aab') is None
    True
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> (r('aaa'), r('aa'))
    (3, 2)
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> (r('aaa', full=False), r('aa', full=False))
    (2, 2)
    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, string, full=True, _string=None, _success=None):
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string
        _success = {} if _success is None else _success

        lengths = [self[0](string, full=full, _string=_string, _success=_success)]
        if lengths[-1] is None:
            string = chain(_string[()], string)
            return self[1](string, full=full, _string=_string, _success=_success)

        string = chain(_string[()], string)
        _string_ = {}
        _success_ = {}
        lengths.append(self[1](string, full=full, _string=_string_, _success=_success_))

        # The cases where `lengths [0] is None` are handled by the recursive call on line 246.
        if lengths[1] is None:
            length = lengths[0]
            if not full:
                _string[()] = chain(_string_[()], string)
                _success[()] = _success[()]
                return length
            else:
                string = _success[()]
                _string__ = {}
                result = emp()(string, full=True, _string=_string__)
                _string[()] = chain(_string_[()], chain(_string__[()], string))
                _success[()] = chain(_string__[()], string) if result == 0 else None
                return length if result == 0 else None
        else: # Both succeeded (all other cases handled in recursive call on line 246).
            if not full:
                _string[()] = chain(_string_[()], string)
                _success[()] = _success[()] if lengths[0] > lengths[1] else _success_[()]
                return max(lengths)
            else:
                string = _success[()] if lengths[0] > lengths[1] else _success_[()]
                _string__ = {}
                result = emp()(string, full=True, _string=_string__)
                _string[()] = chain(_string_[()], chain(_string__[()], string))
                _success[()] = chain(_string__[()], string) if result == 0 else None
                return max(lengths) if result == 0 else None

class rep(are):
    """
    Repetition operation node (zero or more times) for a
    regular expression.

    >>> r = rep(lit('a'))
    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    >>> all([r('a'*i) == i for i in range(100)])
    True
    >>> all([r('a'*i + 'b', full=False) == i for i in range(100)])
    True
    >>> {r('a'*i + 'b') for i in range(10)}
    {None}
    >>> r = con(lit('a'), rep(lit('b')))
    >>> r('a' + 'b'*10)
    11
    >>> r = con(rep(lit('a')), lit('b'))
    >>> r('aaab')
    4
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string, full=True, _string=None, _success=None):
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string
        _success = {} if _success is None else _success

        _strings = []
        _strings.append({})
        lengths = 0
        length = self[0](string, full=False, _string=_strings[-1])
        while length is not None:
            _strings.append({})
            lengths += length
            length = self[0](string, full=False, _string=_strings[-1])

        # Restore after last attempt.
        string = chain(_strings[-1][()], string)
        _strings.pop()

        if not full:
            _string[()] = chain(*([s[()] for s in _strings] + [string]))
            _success[()] = string
            return lengths
        else:
            _string__ = {}
            result = emp()(string, full=True, _string=_string__)
            if result == 0:
                _string[()] = chain(*([s[()] for s in _strings] + [string]))
                _success[()] = string
                return lengths
            # Restore string if above check failed.
            string = chain(_string__[()], string)
            _string[()] = chain(*([s[()] for s in _strings] + [string]))
            return None

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
