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

    class random():
        '''
        Methods for generating random expressions in different ways.
        '''

        @staticmethod
        def size(size = 1, literals = ['a']):
            if size == 1:
                return random.choice([are.emp(), are.lit(random.choice(literals))])
            elif size == 2:
                return are.random.size(size - 1, literals).star()
            elif size >= 3:
                size -= 1
                (op, diff) = (random.randint(0,3), random.randint(1, size - 1))
                if op == 0:
                    return are.random.size(size, literals).star()
                elif op == 1:
                    return are.random.size(size - diff, literals) + are.random.size(diff, literals)
                elif op == 2:
                    return are.random.size(size - diff, literals) | are.random.size(diff, literals)
                elif op == 3:
                    return are.random.size(size - diff, literals) & are.random.size(diff, literals)

    class exhaustive():
        '''
        Methods for generating random expressions in different ways.
        '''

        @staticmethod
        def size(size = 1, literals = ['a']):
            if size == 1:
                return [are.emp()] + [are.lit(literal) for literal in literals]
            elif size == 2:
                return [r.star() for r in are.exhaustive.size(size - 1, literals)]
            elif size >= 3:
                size -= 1
                (op, diff) = (random.randint(0,3), random.randint(1, size - 1))
                rs = [r.star() for r in are.exhaustive.size(size, literals)]
                for diff in range(1, size):
                    r_size_minus_diff = are.exhaustive.size(size - diff, literals)
                    r_diff = are.exhaustive.size(diff, literals)
                    rs.extend([r1 + r2 for r1 in r_size_minus_diff for r2 in r_diff])
                    rs.extend([r1 | r2 for r1 in r_size_minus_diff for r2 in r_diff])
                    rs.extend([r1 & r2 for r1 in r_size_minus_diff for r2 in r_diff])
                return rs

emp = are.emp
lit = are.lit

if __name__ == "__main__":
    doctest.testmod()
