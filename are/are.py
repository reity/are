"""Abstract regular expressions.

Library for working with regular expressions as abstract\
mathematical objects.
"""

from __future__ import annotations
import doctest

class operation(str):
    '''
    Abstract data structure for an operation.
    '''
    pass

class are(dict):
    '''
    Abstract data structure for a regular expression.
    '''

    def star(self: are) -> are:
        return are({operation('star'): [self]})

    def __add__(self: are, other: are) -> are:
        return are({operation('con'): [self, other]})

    def __or__(self: are, other: are) -> are:
        return are({operation('alt'): [self, other]})

    def __and__(self: are, other: are) -> are:
        return are({operation('and'): [self, other]})

if __name__ == "__main__":
    doctest.testmod()
