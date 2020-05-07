"""Abstract regular expressions.

Library for working with regular expressions as abstract\
mathematical objects.
"""

from __future__ import annotations
import itertools
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

    @staticmethod
    def random(size = 1, literals = ['a']):
        '''
        Method for generating random expressions.
        '''
        if size == 1:
            return random.choice([are.emp(), are.lit(random.choice(literals))])
        elif size == 2:
            return are.random(size - 1, literals).star()
        elif size >= 3:
            size -= 1
            (op, diff) = (random.randint(0,3), random.randint(1, size - 1))
            if op == 0:
                return are.random(size, literals).star()
            elif op == 1:
                return are.random(size - diff, literals) + are.random(diff, literals)
            elif op == 2:
                return are.random(size - diff, literals) | are.random(diff, literals)
            elif op == 3:
                return are.random(size - diff, literals) & are.random(diff, literals)

    @staticmethod
    def exhaustive(size = 1, literals = ['a']):
        '''
        Method for creating an exhaustive list of all expressions.
        '''
        if size == 1:
            return [are.emp()] + [are.lit(literal) for literal in literals]
        elif size == 2:
            return [r.star() for r in are.exhaustive(size - 1, literals)]
        elif size >= 3:
            size -= 1
            (op, diff) = (random.randint(0,3), random.randint(1, size - 1))
            rs = [r.star() for r in are.exhaustive(size, literals)]
            for diff in range(1, size):
                r_size_minus_diff = are.exhaustive(size - diff, literals)
                r_diff = are.exhaustive(diff, literals)
                rs.extend([r1 + r2 for r1 in r_size_minus_diff for r2 in r_diff])
                rs.extend([r1 | r2 for r1 in r_size_minus_diff for r2 in r_diff])
                rs.extend([r1 & r2 for r1 in r_size_minus_diff for r2 in r_diff])
            return rs

    def __contains__(self, s, rest = None):
        '''
        Determine whether the supplied string is matched by the
        regular expression. For Kleene star and alternation, as
        much of the string as possible is consumed. For intersection,
        both regular expressions must consume the same number of
        string characters in order for the overall intersection
        expression to match a string.
        '''
        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            return False

        elif o == 'lit':
            s0 = list(self.values())[0][0]
            if s.startswith(s0):
                if rest is not None:
                    rest[0] = s[len(s0):]
                    return True
                else:
                    return len(s) == len(s0)
            else:
                return False

        elif o == 'star':
            contained = True
            while contained:
                rest_ = [None]
                contained = vs[0].__contains__(s, rest_)
                if contained:
                    s = rest_[0]

            if rest is not None:
                rest[0] = s
                return True
            else:
                return len(s) == 0

            return True

        elif o == 'con':
            (a1, a2) = vs

            rest_ = [None]
            if a1.__contains__(s, rest_):
                s = rest_[0]
            else:
                return False

            rest_ = [None]
            if a2.__contains__(s, rest_):
                s = rest_[0]
            else:
                return False

            if rest is not None:
                rest[0] = s
                return True
            else:
                return len(s) == 0

            return True

        elif o == 'alt':
            (a1, a2) = vs
            rest_ = [None]
            (s1, s2) = (None, None)
            
            if a1.__contains__(s, rest_):
                s1 = rest_[0]
            if a2.__contains__(s, rest_):
                s2 = rest_[0]
            
            if s1 is None and s2 is None:
                return False
            elif s1 is not None and s2 is None:
                if rest is not None:
                    rest[0] = s1
                    return True
                else:
                    return len(s1) == 0
            elif s1 is None and s2 is not None:
                if rest is not None:
                    rest[0] = s2
                    return True
                else:
                    return len(s2) == 0
            else:
                if len(s1) <= len(s2):
                    if rest is not None:
                        rest[0] = s1
                        return True
                    else:
                        return len(s1) == 0
                else:
                    if rest is not None:
                        rest[0] = s2
                        return True
                    else:
                        return len(s2) == 0

        elif o == 'and':
            (a1, a2) = vs
            rest_ = [None]
            (s1, s2) = (None, None)

            if a1.__contains__(s, rest_):
                s1 = rest_[0]
            if a2.__contains__(s, rest_):
                s2 = rest_[0]

            if s1 is not None and s2 is not None and len(s1) == len(s2):
                if rest is not None:
                    rest[0] = s1
                    return True
                else:
                    return len(s1) == 0

            else:
                return False

    def finite(self):
        '''
        Determine whether the set of strings that satisfy this regular
        expression is finite. Store the result for future retrieval,
        and return it if it has already been computed.
        '''
        if hasattr(self, '_finite'):
            return self._finite

        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            self._finite = True
        elif o == 'lit':
            self._finite = True
        elif o == 'star':
            self._finite = False
        elif o == 'con':
            (a1, a2) = vs
            self._finite = a1.finite() and a2.finite()
        elif o == 'alt':
            (a1, a2) = vs
            self._finite = a1.finite() and a2.finite()
        elif o == 'and':
            (a1, a2) = vs
            self._finite = a1.finite() or a2.finite()

        return self._finite

    def quantity_ub(self):
        '''
        Determine the upper bound on the number of strings that satisfy this
        regular expression. Store the result for future retrieval, and return
        it if it has already been computed.
        '''
        if hasattr(self, '_quantity_ub'):
            return self._quantity_ub

        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            self._quantity_ub = 0
        elif o == 'lit':
            self._quantity_ub = 1
        elif o == 'star':
            a0 = vs[0]
            self._quantity_ub = float('inf') if a0.quantity_ub() > 0 else 1
        elif o == 'con':
            (a1, a2) = vs
            self._quantity_ub = a1.quantity_ub() * a2.quantity_ub()
        elif o == 'alt':
            (a1, a2) = vs
            self._quantity_ub = a1.quantity_ub() + a2.quantity_ub()
        elif o == 'and':
            (a1, a2) = vs
            self._quantity_ub = max(a1.quantity_ub(), a2.quantity_ub())

        return self._quantity_ub

    def quantity_lb(self):
        '''
        Determine the lower bound on the number of strings that satisfy this
        regular expression. Store the result for future retrieval, and return
        it if it has already been computed.
        '''
        if hasattr(self, '_quantity_lb'):
            return self._quantity_lb

        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            self._quantity_lb = 0
        elif o == 'lit':
            self._quantity_lb = 1
        elif o == 'star':
            a0 = vs[0]
            self._quantity_lb = float('inf') if a0.quantity_lb() > 0 else 1
        elif o == 'con':
            (a1, a2) = vs
            self._quantity_lb = a1.quantity_lb() * a2.quantity_lb()
        elif o == 'alt':
            (a1, a2) = vs
            self._quantity_lb = max(a1.quantity_lb(), a2.quantity_lb())
        elif o == 'and':
            (a1, a2) = vs
            self._quantity_lb = min(a1.quantity_lb(), a2.quantity_lb())

        return self._quantity_lb


    def length_ub(self):
        '''
        Determine the upper bound on the length of any string that satisfies
        this regular expression. Store the result for future retrieval, and
        return it if it has already been computed.
        '''
        if hasattr(self, '_length_ub'):
            return self._length_ub

        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            self._length_ub = None
        elif o == 'lit':
            self._length_ub = len(vs[0])
        elif o == 'star':
            a0 = vs[0]
            self._length_ub = float('inf') if a0.length_ub() > 0 else 0
        elif o == 'con':
            (a1, a2) = vs
            self._length_ub = a1.length_ub() + a2.length_ub()
        elif o == 'alt':
            (a1, a2) = vs
            self._length_ub = max(a1.length_ub(), a2.length_ub())
        elif o == 'and':
            (a1, a2) = vs
            self._length_ub = min(a1.length_ub(), a2.length_ub())

        return self._length_ub

    def length_lb(self):
        '''
        Determine the lower bound on the length of any string that satisfies
        this regular expression. Store the result for future retrieval, and
        return it if it has already been computed.
        '''
        if hasattr(self, '_length_lb'):
            return self._length_lb

        o = list(self.keys())[0]
        vs = list(self.values())[0]
        if o == 'emp':
            self._length_lb = None
        elif o == 'lit':
            self._length_lb = len(vs[0])
        elif o == 'star':
            a0 = vs[0]
            self._length_lb = 0
        elif o == 'con':
            (a1, a2) = vs
            self._length_lb = a1.length_lb() + a2.length_lb()
        elif o == 'alt':
            (a1, a2) = vs
            self._length_lb = min(a1.length_lb(), a2.length_lb())
        elif o == 'and':
            (a1, a2) = vs
            self._length_lb = max(a1.length_lb(), a2.length_lb())

        return self._length_lb

    def strings(self, length = None):
        if length is None:
            for length in itertools.count():
                for s in self.strings(length):
                    yield s
        else:
            o = list(self.keys())[0]
            vs = list(self.values())[0]
            if o == 'emp':
                pass # No strings accepted.
            elif o == 'lit':
                s = list(self.values())[0][0]
                if length == len(s):
                    yield s
            elif o == 'star':
                tmp = are.lit('')
                for i in range(0, length):
                    for s in tmp.strings(length):
                        yield s
                    tmp = tmp + vs[0]
            elif o == 'con':
                for i in range(0,length):
                    for s1 in vs[0].strings(i):
                        for s2 in vs[1].strings(length - i):
                            yield s1 + s2
            elif o == 'alt':
                for s in vs[0].strings(length):
                    yield s
                for s in vs[1].strings(length):
                    if not (s in vs[0]):
                        yield s
            elif o == 'and':
                for s in vs[0].strings(length):
                    if s in vs[1]:
                        yield s

emp = are.emp
lit = are.lit

if __name__ == "__main__":
    doctest.testmod()
