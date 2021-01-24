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

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install are

The library can be imported in the usual way::

    import are
    from are import *

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
