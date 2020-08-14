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
    (0, 0)
    """
    def __new__(cls):
        return super().__new__(cls)

    def __call__(self, string):
        return 0

class lit(are):
    """
    Literal node (individual symbol as a base case) of a regular
    expression instance.

    >>> (lit("a")(""), lit("a")("a"))
    (0, 1)
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, string):
        for symbol in string:
            if symbol == self[0]:
                return 1
        return 0

class con(are):
    """
    Concatenation operation node for two regular expressions.

    >>> r = con(lit('a'), lit('b'))
    >>> (r('ab'), r('cd'))
    (2, 0)
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, s):
        length_0 = self[0](s)
        if length_0 is not None:
            length_1 = self[1](s[length_0:])
            return length_0 + length_1
        return 0

class alt(are):
    """
    Alternation operation node for two regular expressions.

    >>> r = alt(lit('a'), lit('b'))
    >>> (r('a'), r('b'), r('c'))
    (1, 1, 0)
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def __call__(self, s):
        length_0 = self[0](s)
        length_1 = self[1](s)
        return max(length_0, length_1)

class rep(are):
    """
    Repetition operation node (zero or more times) for a
    regular expression.

    >>> r = rep(lit('a'))
    >>> all([r('a'*i) == i for i in range(100)])
    True
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def __call__(self, s):
        lengths = 0
        length = self[0](s)
        while length is not None and len(s) > lengths:
            lengths += length
            length = self[0](s[lengths:])
        return lengths

if __name__ == "__main__":
    doctest.testmod()
