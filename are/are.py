"""Abstract regular expressions.

Library for working with regular expressions as abstract\
mathematical objects.
"""

from __future__ import annotations
import random
import doctest

class operation(str):
    '''
    Abstract data structure for an operation.
    '''
    pass

op = operation

class are(dict):
    '''
    Abstract data structure for a regular expression.
    '''

    @staticmethod
    def emp() -> are:
        return are({operation('emp'): []})

    @staticmethod
    def lit(value = '') -> are:
        return are({operation('lit'): [value]})

    def star(self: are) -> are:
        return are({operation('star'): [self]})

    def __add__(self: are, other: are) -> are:
        return are({operation('con'): [self, other]})

    def __or__(self: are, other: are) -> are:
        return are({operation('alt'): [self, other]})

    def __and__(self: are, other: are) -> are:
        return are({operation('and'): [self, other]})

    def embedded(self):
        o = list(self.keys())[0]
        if o == 'emp':
            return 'emp()'
        elif o == 'lit':
            return 'lit(' + str(list(self.values())[0][0]) + ')'
        elif o == 'star':
            return '(' + self[o][0].embedded() + ').star()'
        elif o == 'con':
            return '(' + (" + ".join(a.embedded() for a in self[o])) + ')'
        elif o == 'alt':
            return '(' + (" | ".join(a.embedded() for a in self[o])) + ')'
        elif o == 'and':
            return '(' + (" & ".join(a.embedded() for a in self[o])) + ')'

emp = are.emp
lit = are.lit

if __name__ == "__main__":
    doctest.testmod()
