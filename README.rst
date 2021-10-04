===
are
===

Library for defining and working with abstract regular expressions that support strings/sequences with elements of any symbol type, with an emphasis on supporting scenarios in which it is necessary to work with regular expressions as abstract mathematical objects.

|pypi| |travis| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/are.svg
   :target: https://badge.fury.io/py/are
   :alt: PyPI version and link.

.. |travis| image:: https://travis-ci.com/reity/are.svg?branch=main
   :target: https://travis-ci.com/reity/are

.. |coveralls| image:: https://coveralls.io/repos/github/reity/are/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/are?branch=main

Purpose
-------
This library provides classes that enable concise construction of abstract regular expressions. In the case of this library, the term *abstract* refers to the fact that the symbols that constitute the "strings" (*i.e.*, iterable sequences) that satisfy an abstract regular expression can be values or objects of any immutable type. Thus, this library also makes it possible to determine whether an iterable containing zero or more objects satisfies a given abstract regular expression. Any abstract regular expression can also be converted into a nondeterministic finite automaton (as implemented within the `PyPI <https://pypi.org/project/nfa/>`_ package) that accepts exactly those iterables which satisfy that abstract regular expression.

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install are

The library can be imported in the usual way::

    import are
    from are import *

Examples
^^^^^^^^
This library makes it possible to construct abstract regular expressions that work with a chosen symbol type. In the example below, a regular expression is defined (using only the literal and concatenation operators) in which symbols are integers. It is then applied to an iterable of integers. This returns the iterable's length (as an integer) if that iterable satisfies the abstract regular expression::

    >>> from are import *
    >>> a = con(lit(1), con(lit(2), lit(3)))
    >>> a([1, 2, 3])
    3

If the longest prefix of an iterable that satisfies an abstract regular expression is desired, the ``full`` parameter can be set to ``False``::

    >>> a([1, 2, 3, 4, 5], full=False)
    3

Operators for alternation and repetition of abstract regular expressions are also available::

    >>> a = rep(con(lit(1), lit(2)))
    >>> a([1, 2, 1, 2, 1, 2])
    6
    >>> a = alt(rep(lit(2)), rep(lit(3)))
    >>> a([2, 2, 2, 2, 2])
    5
    >>> a([3, 3, 3, 3])
    4

The ``emp`` constructor can be used to create an abstract regular expression that is satisfied by the empty iterable::

    >>> a = emp()
    >>> a([])
    0

The ``nul`` constructor can be used to create an abstract regular expression that cannot be satisfied::

    >>> a = nul()
    >>> a([]) is None
    True
    >>> a([1, 2, 3]) is None
    True

An abstract regular expression that has only string symbols can be converted into a regular expression string that is compatible with the built-in `re <https://docs.python.org/3/library/re.html>`_ library::

    >>> a = alt(lit('x'), rep(lit('y')))
    >>> r = a.to_re()
    >>> r
    '(((x)*)|((y)*))'
    >>> import re
    >>> r = re.compile(a.to_re())
    >>> r.fullmatch('yyy')
    <re.Match object; span=(0, 3), match='yyy'>

An abstract regular expression can also be converted into an NFA representation (as implemented within the `PyPI <https://pypi.org/project/nfa/>`_ package)::

    >>> a = con(lit(1), con(lit(2), lit(3)))
    >>> a.to_nfa()
    nfa({1: nfa({2: nfa({3: nfa()})})})

Documentation
-------------
.. include:: toc.rst

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org/>`_::

    cd docs
    python -m pip install -r requirements.txt
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. ../setup.py && make html

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `nose <https://nose.readthedocs.io/>`_ (see ``setup.cfg`` for configution details)::

    nosetests

The subset of the unit tests included in the module itself can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python are/are.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint are

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
Beginning with version 0.1.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
