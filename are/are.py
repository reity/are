"""Abstract regular expressions.

Library for defining and working with abstract regular
expressions that work with any symbol type, with an emphasis
on supporting scenarios in which it is necessary to work with
regular expressions as abstract mathematical objects.
"""

from __future__ import annotations
import doctest
from typing import Optional
from collections.abc import Iterable
from reiter import reiter
from nfa import nfa, epsilon

class are(tuple): # pylint: disable=E1101
    """
    Base class for abstract regular expression instances
    (and nodes of the tree data structure that represents
    abstract regular expression instances).
    """
    def to_nfa(self: are, _nfa: nfa = None) -> nfa:
        """
        Build equivalent NFA from the abstract regular expression instance.
        """
        _nfa_ = None
        _nfa = nfa() if _nfa is None else _nfa

        if isinstance(self, emp):
            _nfa_ = _nfa
        elif isinstance(self, lit):
            _nfa_ = nfa({self[0]: _nfa})
        elif isinstance(self, con):
            _nfa_ = self[0].to_nfa(self[1].to_nfa(_nfa))
        elif isinstance(self, alt):
            _nfa_ = nfa({epsilon: [
                self[0].to_nfa(_nfa),
                self[1].to_nfa(_nfa)
            ]})
        elif isinstance(self, rep):
            _nfa_ = nfa({epsilon: [_nfa]})
            _nfa_[epsilon].append(self[0].to_nfa(_nfa_))

        return _nfa_

    def compile(self: are) -> are:
        """
        Build equivalent NFA and store it internally as an attribute
        for more efficient matching, returning the original abstract
        regular expression instance.
        """
        self._compiled = self.to_nfa().compile() # Compile NFA into transition table.
        return self

    def to_re(self: are) -> str:
        """
        Build equivalent regular expression string that is compatible
        with the built-in `re` module.

        >>> rep(alt(con(lit('a'), lit('b')), emp())).to_re()
        '((((a)(b))|)*)'
        >>> rep(alt(con(lit(123), lit(456)), emp())).to_re()
        Traceback (most recent call last):
          ...
        TypeError: all symbols must be strings
        """
        if isinstance(self, emp):
            re_ = ''
        elif isinstance(self, lit):
            if not isinstance(self[0], str):
                raise TypeError('all symbols must be strings')
            re_ = '(' + self[0] + ')'
        elif isinstance(self, con):
            re_ = '(' + self[0].to_re() + self[1].to_re() + ')'
        elif isinstance(self, alt):
            re_ = '(' + self[0].to_re() + '|' + self[1].to_re() + ')'
        elif isinstance(self, rep):
            re_ = '(' + self[0].to_re() + '*)'

        return re_

    def __call__(self: are, string, full: bool = True, _index: int = 0) -> Optional[int]:
        """
        Determine whether a sequence of symbols (i.e., an abstract string)
        is in the language defined by this regular expression instance.
        """
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        # Determine the length of the longest match either using the compiled
        # NFA (if it is present) or the instance itself.
        # pylint: disable=E1101
        return (
            self._compiled(string, full=full) \
            if hasattr(self, "_compiled") and self._compiled is not None else \
            self._match(string, full, _index)
        )

    def __str__(self):
        """
        Return string representation of instance.
        """
        return\
            type(self).__name__ +\
            (str(tuple(self)) if len(self) != 1 else str(tuple(self))[:-2] + ')')

    def __repr__(self):
        """
        Return string representation of instance.

        >>> rep(alt(con(lit('a'), lit('b')), emp()))
        rep(alt(con(lit('a'), lit('b')), emp()))
        """
        return str(self)

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
    >>> r = emp().compile()
    >>> (r(""), r("abc"))
    (0, None)
    """
    def __new__(cls):
        return super().__new__(cls)

    # pylint: disable=R0201
    def _match(self: are, string, full: bool, _index: int) -> Optional[int]:
        try:
            symbol = string[_index] # pylint: disable=W0612
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
    >>> r = lit("a").compile()
    >>> (r("a"), r(""))
    (1, None)
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def _match(self: are, string, full: bool, _index: int) -> Optional[int]:
        try:
            symbol = string[_index]

            if symbol == self[0]:
                if not full:
                    return 1
                else:
                    result = emp()._match(string, full=True, _index=(_index + 1))
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
    >>> r = con(lit('a'), lit('b')).compile()
    >>> (r('ab'), r('a'), r('abc'), r('cd'))
    (2, None, None, None)
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def _match(self: are, string, full: bool, _index: int) -> Optional[int]:
        lengths = self[0]._match(string, full=False, _index=_index)

        if lengths is not None:
            length = self[1]._match(string, full=False, _index=(_index + lengths))
            if length is not None:
                lengths += length

                if not full:
                    return lengths
                else:
                    result = emp()._match(string, full=True, _index=(_index + lengths))
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
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> r = r.compile()
    >>> (r('aaa'), r('aa'), r('a'))
    (3, 2, None)
    """
    def __new__(cls, *arguments):
        return super().__new__(cls, [*arguments])

    def _match(self: are, string, full: bool, _index: int) -> Optional[int]:
        lengths = [self[0]._match(string, full=full, _index=_index)]
        if lengths[-1] is None:
            return self[1]._match(string, full=full, _index=_index)

        lengths.append(self[1]._match(string, full=full, _index=_index))

        # The cases where `lengths [0] is None` are handled by the recursive call on line 226.
        if lengths[1] is None:
            length = lengths[0]
            if not full:
                return length
            else:
                result = emp()._match(string, full=True, _index=(_index + length))
                return length if result == 0 else None
        else: # Both succeeded (all other cases handled in recursive call on line 226).
            if not full:
                return max(lengths)
            else:
                length = max(lengths)
                result = emp()._match(string, full=True, _index=(_index + length))
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
    >>> r = con(rep(lit('a')), lit('b')).compile()
    >>> r('aaab')
    4
    >>> r = rep(lit('a')).compile()
    >>> all([r('a'*i) == i for i in range(100)])
    True
    """
    def __new__(cls, argument):
        return super().__new__(cls, [argument])

    def _match(self: are, string, full: bool, _index: int) -> Optional[int]:
        lengths = 0
        length = self[0]._match(string, full=False, _index=_index)
        while length is not None:
            lengths += length
            length = self[0]._match(string, full=False, _index=(_index + lengths))

        if not full:
            return lengths
        else:
            result = emp()._match(string, full=True, _index=(_index + lengths))
            if result == 0:
                return lengths

        return None # String does not satisfy the regular expression.

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
