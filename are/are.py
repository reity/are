"""Abstract regular expressions.

Library for working with regular expressions as abstract
mathematical objects.
"""

from __future__ import annotations
import doctest

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

    >>> (emp()(""), emp()("ab"))
    (0, None)
    >>> emp()("abc", full=False)
    0
    """
    def __new__(cls):
        return super().__new__(cls)

    def __call__(self, string, full=True):
        return 0 if not full or len(string) == 0 else None

class lit(are):
    """
    Literal node (individual symbol as a base case) of a regular
    expression instance.

    >>> (lit("a")(""), lit("a")("a"), lit("a")("ab"))
    (None, 1, None)
    >>> (lit("a")("", full=False), lit("a")("ab", full=False))
    (None, 1)
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string, full=True):
        for symbol in string:
            if symbol == self[0]:
                return 1 if not full or len(string) == 1 else None
            break # Only check the first symbol.

        return None # String does not satisfy the regular expression.

class con(are):
    """
    Concatenation operation node for two regular expressions.

    >>> r = con(lit('a'), lit('b'))
    >>> (r('ab'), r('a'), r('abc'), r('cd'))
    (2, None, None, None)
    >>> (r('a', full=False), r('abc', full=False), r('cd', full=False))
    (None, 2, None)
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, s, full=True):
        lengths = self[0](s, full=False)
        if lengths is not None and len(s) >= lengths:
            if (length := self[1](s[lengths:], full=False)) is not None:
                lengths += length
                return lengths if not full or len(s) == lengths else None

        return None # String does not satisfy the regular expression.

class alt(are):
    """
    Alternation operation node for two regular expressions.

    >>> r = alt(lit('a'), lit('b'))
    >>> (r('a'), r('b'), r('c'))
    (1, 1, None)
    >>> r('ac', full=False)
    1
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, s, full=True):
        lengths = [self[0](s, full=full)]
        if lengths[-1] is None:
            return self[1](s, full=full)

        lengths.append(self[1](s, full=full))
        if lengths[-1] is None:
            return lengths[0]

        length = max(lengths)
        return length if not full or len(s) == length else None

class rep(are):
    """
    Repetition operation node (zero or more times) for a
    regular expression.

    >>> r = rep(lit('a'))
    >>> all([r('a'*i) == i for i in range(100)])
    True
    >>> all([r('a'*i + 'b', full=False) == i for i in range(100)])
    True
    >>> {r('a'*i + 'b') for i in range(10)}
    {None}
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, s, full=True):
        lengths = 0
        length = self[0](s, full=False)
        while length is not None and len(s) >= lengths:
            lengths += length
            length = self[0](s[lengths:], full=False)

        return lengths if not full or len(s) == lengths else None

if __name__ == "__main__":
    doctest.testmod()
