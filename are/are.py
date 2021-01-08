"""Abstract regular expressions.

Library for defining and working with abstract regular
expressions that work with any symbol type, with an emphasis
on supporting scenarios in which it is necessary to work with
regular expressions as abstract mathematical objects.
"""

from __future__ import annotations
import doctest
from collections.abc import Iterable
from reiter import reiter

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
    >>> emp()(iter("ab")) is None
    True
    >>> emp()("abc", full=False)
    0
    >>> emp()(iter("abc"), full=False)
    0
    """
    def __new__(cls):
        return super().__new__(cls)

    def __call__(self, string, full=True, _index=0):
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        try:
            symbol = string[_index]
            if not full:
                return 0
            else:
                return None
        except (StopIteration, IndexError):
            return 0

class lit(are):
    """
    Literal node (individual symbol as a base case) of a regular
    expression instance.

    >>> (lit("a")(""), lit("a")("a"), lit("a")("ab"))
    (None, 1, None)
    >>> (lit("a")("", full=False), lit("a")("ab", full=False))
    (None, 1)
    >>> lit("a")(iter("ab"), full=False)
    1
    >>> lit("a")(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string, full=True, _index=0):
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        try:
            symbol = string[_index]

            if symbol == self[0]:
                if not full:
                    return 1
                else:
                    result = emp()(string, full=True, _index=(_index + 1))
                    if result == 0:
                        return 1

            return None # String does not satisfy the regular expression.

        except (StopIteration, IndexError):
            return None

class con(are):
    """
    Concatenation operation node for two regular expressions.

    >>> r = con(lit('a'), lit('b'))
    >>> (r('ab'), r('a'), r('abc'), r('cd'))
    (2, None, None, None)
    >>> (r(iter('ab')), r(iter('a')), r(iter('abc')), r(iter('cd')))
    (2, None, None, None)
    >>> (r('a', full=False), r('abc', full=False), r('cd', full=False))
    (None, 2, None)
    >>> (r(iter('a'), full=False), r(iter('abc'), full=False), r(iter('cd'), full=False))
    (None, 2, None)
    >>> r = con(lit('a'), con(lit('b'), lit('c')))
    >>> (r('abc'), r('abcd', full=False), r('ab'))
    (3, 3, None)
    >>> (r(iter('abc')), r(iter('abcd'), full=False), r(iter('ab')))
    (3, 3, None)
    >>> r = con(con(lit('a'), lit('b')), lit('c'))
    >>> r('abc')
    3
    >>> r(iter('abc'))
    3
    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, string, full=True, _index=0):
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        lengths = self[0](string, full=False, _index=_index)

        if lengths is not None:
            length = self[1](string, full=False, _index=(_index + lengths))
            if length is not None:
                lengths += length

                if not full:
                    return lengths
                else:
                    result = emp()(string, full=True, _index=(_index + lengths))
                    if result == 0:
                        return lengths

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
    >>> r(iter('aab')) is None
    True
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> (r('aaa'), r('aa'))
    (3, 2)
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> (r('aaa', full=False), r('aa', full=False))
    (3, 2)
    >>> (r(iter('aaa'), full=False), r(iter('aa'), full=False))
    (3, 2)
    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, string, full=True, _index=0):
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        lengths = [self[0](string, full=full, _index=_index)]
        if lengths[-1] is None:
            return self[1](string, full=full, _index=_index)

        lengths.append(self[1](string, full=full, _index=_index))

        # The cases where `lengths [0] is None` are handled by the recursive call on line 226.
        if lengths[1] is None:
            length = lengths[0]
            if not full:
                return length
            else:
                result = emp()(string, full=True, _index=(_index + length))
                return length if result == 0 else None
        else: # Both succeeded (all other cases handled in recursive call on line 226).
            if not full:
                return max(lengths)
            else:
                length = max(lengths)
                result = emp()(string, full=True, _index=(_index + length))
                return length if result == 0 else None

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
    >>> all([r(iter('a'*i + 'b'), full=False) == i for i in range(100)])
    True
    >>> {r('a'*i + 'b') for i in range(10)}
    {None}
    >>> {r(iter('a'*i + 'b')) for i in range(10)}
    {None}
    >>> r = con(lit('a'), rep(lit('b')))
    >>> r('a' + 'b'*10)
    11
    >>> r(iter('a' + 'b'*10))
    11
    >>> r = con(rep(lit('a')), lit('b'))
    >>> r('aaab')
    4
    >>> r(iter('aaab'))
    4
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string, full=True, _index=0):
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        lengths = 0
        length = self[0](string, full=False, _index=_index)
        while length is not None:
            lengths += length
            length = self[0](string, full=False, _index=(_index + lengths))

        if not full:
            return lengths
        else:
            result = emp()(string, full=True, _index=(_index + lengths))
            if result == 0:
                return lengths

        return None # String does not satisfy the regular expression.

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
