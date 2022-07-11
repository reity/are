"""
Library for defining and operating on abstract regular expressions that work
with any symbol type, with an emphasis on supporting scenarios in which it is
necessary to work with regular expressions as abstract mathematical objects.
"""
from __future__ import annotations
import doctest
from typing import Optional, Iterable
import collections.abc
from reiter import reiter
from nfa import nfa, epsilon

class are(tuple):
    """
    Base class for abstract regular expression instances (and the individual
    nodes found within an abstract syntax tree instance). Abstract regular
    expressions can contain symbols of any immutable type and can be built up
    using common operators such as concatenation, alternation, and repetition.

    >>> a = con(lit(1), con(lit(2), lit(3)))
    >>> a([1, 2, 3])
    3

    This class is derived from the built-in :class:`tuple <tuple>` type.
    Each instance of this class acts as a node within the abstract syntax tree
    representing an abstract regular expression. The elements inside the instance
    are the child nodes of the node represented by the instance and can be
    accessed in the usual manner supported by the :class:`tuple <tuple>` type.

    >>> a = con(lit(1), con(lit(2), lit(3)))
    >>> a[1]
    con(lit(2), lit(3))
    """
    def to_nfa(self: are, _nfa: nfa = None) -> nfa:
        """
        Convert this abstract regular expression instance into a nondeterministic
        finite automaton (NFA) that accepts the set of iterables that satisfies this
        instance.

        >>> a = con(lit(1), con(lit(2), lit(3)))
        >>> a.to_nfa()
        nfa({1: nfa({2: nfa({3: nfa()})})})
        """
        _nfa_ = None
        _nfa_next = nfa() if _nfa is None else _nfa

        if isinstance(self, nul):
            _nfa_ = None
        elif isinstance(self, emp):
            _nfa_ = _nfa_next
        elif isinstance(self, lit):
            _nfa_ = nfa({self[0]: _nfa_next})
        elif isinstance(self, con):
            _nfa_rhs = self[1].to_nfa(_nfa_next)
            _nfa_ = None if _nfa_rhs is None else self[0].to_nfa(_nfa_rhs)
        elif isinstance(self, alt):
            _nfa_lhs = self[0].to_nfa(_nfa_next)
            _nfa_rhs = self[1].to_nfa(_nfa_next)
            if _nfa_lhs is not None and _nfa_rhs is not None:
                _nfa_ = nfa({epsilon: [_nfa_lhs, _nfa_rhs]})
            elif _nfa_lhs is not None:
                _nfa_ = _nfa_lhs
            elif _nfa_rhs is not None:
                _nfa_ = _nfa_rhs
            else:
                _nfa_ = None
        elif isinstance(self, rep):
            _nfa_ = nfa({epsilon: [_nfa_next]})
            _nfa_arg = self[0].to_nfa(_nfa_)
            if _nfa_arg is not None:
                _nfa_[epsilon].append(_nfa_arg)

        # In the root invocation, ``None`` implies that the NFA instance should
        # reject all strings. Otherwise, return the assembled NFA instance.
        return -nfa() if (_nfa_ is None and _nfa is None) else _nfa_

    def compile(self: are) -> are:
        """
        Convert this instance into an equivalent NFA and store it internally as an
        attribute (to enable more efficient matching). Return the original abstract
        regular expression instance.

        >>> a = alt(lit('x'), rep(con(lit('y'), lit('z'))))
        >>> a = a.compile()
        >>> a(['x'])
        1
        >>> a(['y', 'z', 'y', 'z'])
        4
        """
        setattr(self, '_compiled', self.to_nfa().compile()) # Transition table.
        return self

    def to_re(self: are) -> str:
        """
        If this instance has string symbols (and no other symbols of any other type),
        convert it to an equivalent regular expression string that is compatible
        with the built-in :obj:`re <re>` module.

        >>> rep(alt(con(lit('a'), lit('b')), emp())).to_re()
        '((((a)(b))|)*)'
        >>> rep(alt(con(lit('a'), con(lit('b'), nul())), emp())).to_re()
        '((((a)((b)[^\\\\w\\\\W]))|)*)'

        Any attempt to convert an instance that has non-string symbols raises an
        exception.

        >>> rep(alt(con(lit(123), lit(456)), emp())).to_re()
        Traceback (most recent call last):
          ...
        TypeError: all symbols must be strings
        """
        if isinstance(self, nul):
            re_ = r'[^\w\W]' # Contradiction.
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

    def __call__(self: are, string: Iterable, full: bool = True, _index: int = 0) -> Optional[int]:
        """
        Determine whether an iterable of symbols (*i.e.*, an abstract *string*
        in the formal sense associated with the mathematical definition of a
        regular expression) is in the formal language represented by this instance.
        By default, the length of the abstract string is returned if the abstract
        string satisfies this instance.

        >>> a = rep(con(lit(1), lit(2)))
        >>> a([1, 2, 1, 2, 1, 2])
        6
        >>> a = alt(rep(lit(2)), rep(lit(3)))
        >>> a([2, 2, 2, 2, 2])
        5
        >>> a([3, 3, 3, 3])
        4

        If the supplied abstract string does not satisfy this instance, then ``None``
        is returned.

        >>> a([1, 1, 1]) is None
        True

        If the optional parameter ``full`` is set to ``False``, then the length of
        the longest prefix of the abstract string that satisfies this instance is
        returned. If no prefix satisfies this instance, then ``None`` is returned.

        >>> a = con(lit(1), con(lit(2), lit(3)))
        >>> a([1, 2, 3, 4, 5], full=False)
        3
        >>> a = con(lit(1), con(lit(2), lit(3)))
        >>> a([4, 4, 4], full=False) is None
        True

        If an instance is satisfied by the empty abstract string and ``full`` is set
        to ``False``, then the empty prefix of any abstract string satisfies the
        abstract regular expression instance (and, thus, a successful integer result
        of ``0`` is returned in such cases).

        >>> a = alt(lit(2), emp()) # Satisfied by the empty abstract string.
        >>> a([1, 1, 1], full=False) # Empty string is a prefix of ``[1, 1, 1]``.
        0

        Any attempt to apply an abstract regular expression instance to a
        non-iterable raises an exception.

        >>> nul()(123)
        Traceback (most recent call last):
          ...
        ValueError: input must be an iterable
        """
        if not isinstance(string, (collections.abc.Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        # Determine the length of the longest match either using the compiled
        # NFA (if it is present) or the instance itself.
        return ( # pylint: disable=no-member
            self._compiled(string, full=full)
            if hasattr(self, '_compiled') and self._compiled is not None else
            self._match(string, full, _index)
        )

    def __str__(self: are) -> str:
        """
        Return string representation of instance.

        >>> a = rep(con(lit(1), alt(lit(2), lit(3))))
        >>> str(a)
        'rep(con(lit(1), alt(lit(2), lit(3))))'

        Assuming that this module has been imported in a manner such that the
        :obj:`are` subclasses are associated with the variables as they appear
        in this module (*e.g.*, :obj:`con` is associated with the variable ``con``
        in the relevant scope), the strings returned by this method can be evaluated
        to reconstruct the instance.

        >>> a = rep(con(lit(1), alt(lit(2), lit(3))))
        >>> eval(str(a))
        rep(con(lit(1), alt(lit(2), lit(3))))
        """
        return \
            type(self).__name__ + \
            (str(tuple(self)) if len(self) != 1 else str(tuple(self))[:-2] + ')')

    def __repr__(self: are) -> str:
        """
        Return string representation of instance.

        >>> rep(alt(con(lit('a'), lit('b')), emp()))
        rep(alt(con(lit('a'), lit('b')), emp()))
        """
        return str(self)

class nul(are):
    """
    Singleton class containing an object that corresponds to the sole
    abstract regular expression instance that cannot be satisfied by any
    iterable (*i.e.*, that cannot be satisfied by any abstract string).

    >>> (nul()(iter('ab')), nul()(iter('abc'), full=False))
    (None, None)
    >>> r = nul()
    >>> (r(''), r('abc'), r('', full=False), r('abc', full=False))
    (None, None, None, None)

    More usage examples involving compilation of :obj:`are` instances
    that contain instances of this class are presented below.

    >>> r = r.compile()
    >>> (r(''), r('abc'), r('', full=False), r('abc', full=False))
    (None, None, None, None)
    >>> ((con(nul(), lit('a')))('a'), (con(nul(), lit('a'))).compile()('a'))
    (None, None)
    >>> ((con(lit('a'), nul()))('a'), (con(lit('a'), nul())).compile()('a'))
    (None, None)
    >>> ((alt(nul(), lit('a')))('a'), (alt(nul(), lit('a'))).compile()('a'))
    (1, 1)
    >>> ((alt(lit('a'), nul()))('a'), (alt(lit('a'), nul())).compile()('a'))
    (1, 1)
    >>> ((alt(nul(), nul()))('a'), (alt(nul(), nul())).compile()('a'))
    (None, None)
    >>> (con(rep(nul()), lit('a')).compile())('a')
    1

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> nul()(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls):
        """Instance constructor."""
        return super().__new__(cls)

    # pylint: disable=unused-argument
    def _match(self: are, string: Iterable, full: bool, _index: int):
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        try:
            _ = string[_index] # May consume a symbol.
            return None
        except (StopIteration, IndexError):
            return None

class emp(are):
    """
    Singleton class containing an object that corresponds to the sole
    abstract regular expression instance that is satisfied only by an
    empty iterable (*i.e.*, an abstract string with a length of zero).

    >>> (emp()(''), emp()('ab'))
    (0, None)
    >>> emp()(iter('ab')) is None
    True
    >>> emp()('abc', full=False)
    0
    >>> emp()(iter('abc'), full=False)
    0
    >>> r = emp().compile()
    >>> (r(''), r('abc'))
    (0, None)

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> emp()(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls):
        """Instance constructor."""
        return super().__new__(cls)

    def _match(self: are, string: Iterable, full: bool, _index: int) -> Optional[int]:
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        try:
            _ = string[_index] # May consume a symbol.
            if not full:
                return 0

            return None

        except (StopIteration, IndexError):
            return 0

class lit(are):
    """
    Abstract regular expression instances that are satisfied by exactly one
    symbol. Instances of this class also serve as the leaf nodes (*i.e.*, base
    cases) corresponding to abstract string *literals* (in the formal sense
    associated with the mathematical definition of a regular expression).

    >>> (lit('a')(''), lit('a')('a'), lit('a')('ab'))
    (None, 1, None)
    >>> (lit('a')('', full=False), lit('a')('ab', full=False))
    (None, 1)
    >>> lit('a')(iter('ab'), full=False)
    1
    >>> r = lit('a').compile()
    >>> (r('a'), r(''))
    (1, None)

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> lit('a')(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, argument):
        """Instance constructor."""
        return super().__new__(cls, [argument])

    def _match(self: are, string: Iterable, full: bool, _index: int) -> Optional[int]:
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        try:
            symbol = string[_index]

            if symbol == self[0]:
                if not full:
                    return 1

                # pylint: disable=protected-access
                result = emp()._match(string, full=True, _index=(_index + 1))
                if result == 0:
                    return 1

            return None # Abstract string does not satisfy the regular expression.

        except (StopIteration, IndexError):
            return None

class con(are):
    """
    Concatenation operation for two :obj:`are` instances. Instances of this
    class also serve as the internal nodes of the tree data structure
    representing an abstract regular expression.

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
    >>> r = con(lit('a'), lit('b')).compile()
    >>> (r('ab'), r('a'), r('abc'), r('cd'))
    (2, None, None, None)

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        """Instance constructor."""
        return super().__new__(cls, [*arguments])

    def _match(self: are, string: Iterable, full: bool, _index: int) -> Optional[int]:
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        # pylint: disable=protected-access
        lengths = self[0]._match(string, full=False, _index=_index)

        if lengths is not None:
            length = self[1]._match(string, full=False, _index=(_index + lengths))
            if length is not None:
                lengths += length

                if not full:
                    return lengths

                result = emp()._match(string, full=True, _index=(_index + lengths))
                if result == 0:
                    return lengths

        return None # Abstract string does not satisfy the regular expression.

class alt(are):
    """
    Alternation operation for two :obj:`are` instances. Instances of this
    class also serve as the internal nodes of the tree data structure
    representing an abstract regular expression.

    >>> r = alt(con(lit('a'), lit('a')), lit('a'))
    >>> r('aa')
    2
    >>> r = alt(lit('b'), con(lit('a'), lit('a')))
    >>> r('aa')
    2
    >>> r = con(alt(lit('a'), lit('b')), alt(lit('c'), lit('d')))
    >>> (r('ac'), r('ad'), r('bc'), r('bd'))
    (2, 2, 2, 2)
    >>> r = con(alt(lit('a'), lit('b')), lit('c'))
    >>> (r('ac'), r('bc'), r('c'), r('a'), r('b'))
    (2, 2, None, None, None)
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
    >>> r0 = alt(lit('a'), alt(lit('b'), lit('c')))
    >>> r1 = con(r0, r0)
    >>> {r1(x + y) for x in 'abc' for y in 'abc'}
    {2}
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
    >>> r = alt(con(lit('a'), lit('a')), con(lit('a'), con(lit('a'), lit('a'))))
    >>> r = r.compile()
    >>> (r('aaa'), r('aa'), r('a'))
    (3, 2, None)

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, *arguments):
        """Instance constructor."""
        return super().__new__(cls, [*arguments])

    def _match(self: are, string: Iterable, full: bool, _index: int) -> Optional[int]:
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        # pylint: disable=protected-access

        # Determine whether (and by what length of substring) the first alternative
        # is satisfied.
        lengths = [self[0]._match(string, full=full, _index=_index)]

        if lengths[0] is None:
            # First alternative is not satisfied, so determine separately whether
            # (and by what length of substring) the second alternative is satisfied.
            return self[1]._match(string, full=full, _index=_index)

        # First alternative is satisfied; determine if second alternative is also
        # satisfied (for example, in case it is satisfied by a longer portion of the
        # abstract string).
        lengths.append(self[1]._match(string, full=full, _index=_index))

        if lengths[1] is None:
            # Second alternative is not satisfied, so return the length of the
            # satisfying substring (*unless* it has been specified that the full
            # string must satisfy this instance).
            length = lengths[0]
            if not full:
                return length

            # Ensure that the full string satisfies this instance; otherwise,
            # indicate failure.
            result = emp()._match(string, full=True, _index=(_index + length))
            return length if result == 0 else None

        # Both alternatives succeeded, so return the length of the longer of the
        # two satisfied alternatives (*unless* it has been specified that the full
        # string must satisfy this instance).
        length = max(lengths)
        if not full:
            return length

        # Ensure that the full string satisfies this instance; otherwise,
        # indicate failure.
        result = emp()._match(string, full=True, _index=(_index + length))
        return length if result == 0 else None

class rep(are):
    """
    Repetition operation (zero or more times) for an :obj:`are` instance.
    Instances of this class also serve as the internal nodes of the tree data
    structure representing an abstract regular expression.

    >>> r = rep(lit('a'))
    >>> all([r('a'*i) == i for i in range(100)])
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

    Note that the empty abstract string satisfies any instance of this class.

    >>> r('')
    0
    >>> r('bbbb', full=False)
    0
    >>> all([r('a'*i + 'b', full=False) == i for i in range(100)])
    True
    >>> all([r(iter('a'*i + 'b'), full=False) == i for i in range(100)])
    True

    Any attempt to apply an abstract regular expression instance to a
    non-iterable raises an exception.

    >>> r(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __new__(cls, argument):
        """Instance constructor."""
        return super().__new__(cls, [argument])

    def _match(self: are, string: Iterable, full: bool, _index: int) -> Optional[int]:
        """
        One of an ensemble of mutually recursive matching functions (one function
        per type of base case or internal node of an abstract regular expression).
        Accepts an iterable of symbols and returns the length of the longest matching
        prefix of that string (or ``None``, if the matching criteria are not met).
        These functions are invoked by the :obj:`are.__call__` method of an instance.
        """
        # pylint: disable=protected-access
        lengths = 0
        length = self[0]._match(string, full=False, _index=_index)
        while length is not None:
            lengths += length
            length = self[0]._match(string, full=False, _index=(_index + lengths))

        if not full:
            return lengths

        result = emp()._match(string, full=True, _index=(_index + lengths))
        if result == 0:
            return lengths

        return None # Abstract string does not satisfy the regular expression.

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
