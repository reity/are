===
are
===

Library for defining and working with abstract regular expressions that support strings/sequences with elements of any symbol type, with an emphasis on supporting scenarios in which it is necessary to work with regular expressions as abstract mathematical objects.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/are.svg
   :target: https://badge.fury.io/py/are
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/are/badge/?version=latest
   :target: https://are.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/reity/are/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/reity/are/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/reity/are/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/are?branch=main
   :alt: Coveralls test coverage summary

Purpose
-------
This library provides classes that enable concise construction of abstract regular expressions. In the case of this library, the term *abstract* refers to the fact that the symbols that constitute the abstract *strings* (*i.e.*, iterable sequences) that satisfy an abstract regular expression can be values or objects of any immutable type. Thus, this library also makes it possible to determine whether an iterable containing zero or more objects satisfies a given abstract regular expression. Any abstract regular expression can also be converted into a nondeterministic finite automaton (as implemented within `another package <https://pypi.org/project/nfa/>`__) that accepts exactly those iterables which satisfy that abstract regular expression.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/are>`__::

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

An abstract regular expression that has only string symbols can be converted into a regular expression string that is compatible with the built-in `re <https://docs.python.org/3/library/re.html>`__ library::

    >>> a = alt(lit('x'), rep(lit('y')))
    >>> r = a.to_re()
    >>> r
    '(((x)*)|((y)*))'
    >>> import re
    >>> r = re.compile(a.to_re())
    >>> r.fullmatch('yyy')
    <re.Match object; span=(0, 3), match='yyy'>

An abstract regular expression can also be converted into an NFA representation (as implemented within the `PyPI <https://pypi.org/project/nfa>`__ package)::

    >>> a = con(lit(1), con(lit(2), lit(3)))
    >>> a.to_nfa()
    nfa({1: nfa({2: nfa({3: nfa()})})})

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

The subset of the unit tests included in the module itself can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__::

    python are/are.py -v

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint are test/test_are.py

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/are>`__ for this library.

Versioning
^^^^^^^^^^
Beginning with version 0.1.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/are>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive::

    rm -rf build dist *.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__::

    python -m twine upload dist/*
