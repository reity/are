from importlib import import_module
from itertools import product, islice
from random import sample
import re
from unittest import TestCase

from are.are import *

def api_methods():
    """
    API symbols that should be available to users upon module import.
    """
    return {'are', 'emp', 'lit', 'con', 'alt', 'rep'}

class Test_namespace(TestCase):
    """
    Check that the exported namespace provide access to the expected
    classes and functions.
    """
    def test_module(self):
        module = import_module('are.are')
        self.assertTrue(api_methods().issubset(module.__dict__.keys()))

def strs(alphabet, k):
    """
    Yield all strings of length at most `k` containing
    only the characters in the supplied alphabet of symbols.
    """
    for i in range(k):
        for s in product(*[alphabet]*i):
            yield ''.join(s)

def ares(alphabet):
    """
    Yield a sample of all abstract regular expression instances for the supplied
    alphabet of symbols.
    """
    rs = [emp()] + [lit(s) for s in alphabet]
    while True:
        rs = sample(rs, min(len(rs), 3))
        for (op, arity) in ((con, 2), (alt, 2), (rep, 1)):
            for rs_ in product(*[rs]*arity):
                r = op(*rs_)
                rs.append(r)
                yield r

def longest(re_r, s):
    """
    Find the length of the longest prefix substring that matches a
    regular expression compiled using the `re` module.
    """
    return max(
        (
            max(m.span())
            for i in range(len(s) + 1)
            for m in [re_r.fullmatch(s[:i])] if m is not None
        ),
        default=0
    )

class Test_are(TestCase):
    def test_are(self):
        for r in islice(ares(['a', 'b']), 0, 100):
            for s in strs(['a', 'b'], 5):
                match = r(s)
                self.assertTrue((isinstance(match, int) and match == len(s)) or match is None)

    def test_are_full_false(self):
        for r in islice(ares(['a', 'b']), 0, 100):
            for s in strs(['a', 'b'], 5):
                match = r(s, full=False)
                self.assertTrue((isinstance(match, int) and match <= len(s)) or match is None)

    def test_are_compile(self):
        for r in islice(ares(['a', 'b']), 0, 100):
            for full in (False, True):
                ss = list(strs(['a', 'b'], 5))
                sms_r = set((s, m) for s in ss for m in [r(s, full)])
                rc = r.compile()
                sms_r_compiled = set((s, m) for s in ss for m in [rc(s, full)])
                self.assertEqual(sms_r, sms_r_compiled)

    def test_are_to_re(self):
        for r in islice(ares(['a', 'b']), 0, 100):
            ss = list(strs(['a', 'b'], 5))
            ss_r = set(s for s in ss if r(s) is not None)
            r_re = re.compile(r.to_re())
            ss_r_re = set(s for s in ss if r_re.fullmatch(s) is not None)
            self.assertEqual(ss_r, ss_r_re)

    def test_are_to_re_not_full(self):
        for r in islice(ares(['a', 'b']), 0, 100):
            ss = list(strs(['a', 'b'], 5))
            sms_r = set((s, m) for s in ss for m in [r(s, False)] if m is not None)
            r_re = re.compile(r.to_re())
            sms_r_re = set((s, longest(r_re, s)) for (s, _) in sms_r)
            self.assertEqual(sms_r, sms_r_re)
