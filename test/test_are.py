"""
Test suite in which functional unit tests for matching, compilation, and
conversion methods are applied to a sample of a bounded subset of all
possible data structure instances.
"""
from __future__ import annotations
from typing import Sequence, Iterable
from importlib import import_module
from itertools import product, islice
from random import sample
import re
from unittest import TestCase

from are.are import are, nul, emp, lit, con, alt, rep

def api_methods():
    """
    API symbols that should be available to users upon module import.
    """
    return {'are', 'nul', 'emp', 'lit', 'con', 'alt', 'rep'}

class Test_namespace(TestCase):
    """
    Check that the exported namespace provide access to the expected
    classes and subclasses.
    """
    def test_module(self):
        """
        Check namespace against reference list of classes.
        """
        module = import_module('are.are')
        self.assertTrue(api_methods().issubset(module.__dict__.keys()))

def strs(alphabet: Sequence[str], k: int) -> Iterable[str]:
    """
    Yield all strings of length at most ``k`` containing
    only the characters in the supplied alphabet of symbols.
    """
    for i in range(k):
        for s in product(*[alphabet]*i):
            yield ''.join(s)

def ares(alphabet: Sequence[str]) -> Iterable[are]:
    """
    Yield a sample of all abstract regular expression instances
    for the supplied alphabet of symbols.
    """
    rs = [nul(), emp()] + [lit(s) for s in alphabet]
    while True:
        rs = sample(rs, min(len(rs), 3))
        for (op, arity) in ((con, 2), (alt, 2), (rep, 1)):
            for rs_ in product(*[rs]*arity):
                r = op(*rs_)
                rs.append(r)
                yield r

def longest(re_r: re.Pattern, s: str) -> int:
    """
    Find the length of the longest prefix substring that matches a
    regular expression compiled using the ``re`` module.
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
    """
    Functional unit tests for the abstract regular expression class, its
    subclasses, and their methods.
    """
    def test_are(self):
        """
        Tests of matching method.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            for s in strs(['a', 'b'], 5):
                match = r(s)
                self.assertTrue((isinstance(match, int) and match == len(s)) or match is None)

    def test_are_full_false(self):
        """
        Tests of matching method when matching a prefix of the string is permitted.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            for s in strs(['a', 'b'], 5):
                match = r(s, full=False)
                self.assertTrue((isinstance(match, int) and match <= len(s)) or match is None)

    def test_are_compile(self):
        """
        Tests of compilation method that converts an instance to an NFA, with
        confirmation that matching behavior is preserved.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            for full in (False, True):
                ss = list(strs(['a', 'b'], 5))
                sms_r = set((s, m) for s in ss for m in [r(s, full)])
                rc = r.compile()
                sms_r_compiled = set((s, m) for s in ss for m in [rc(s, full)])
                self.assertEqual(sms_r, sms_r_compiled)

    def test_are_to_re(self):
        """
        Tests of method that converts to built-in Python regular expressions.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            ss = list(strs(['a', 'b'], 5))
            ss_r = set(s for s in ss if r(s) is not None)
            r_re = re.compile(r.to_re())
            ss_r_re = set(s for s in ss if r_re.fullmatch(s) is not None)
            self.assertEqual(ss_r, ss_r_re)

    def test_are_to_re_not_full(self):
        """
        Tests of method that converts to built-in Python regular expressions,
        with comparison of partial matching behaviors between the two.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            ss = list(strs(['a', 'b'], 5))
            sms_r = set((s, m) for s in ss for m in [r(s, False)] if m is not None)
            r_re = re.compile(r.to_re())
            sms_r_re = set((s, longest(r_re, s)) for (s, _) in sms_r)
            self.assertEqual(sms_r, sms_r_re)

    def test_are_to_nfa(self):
        """
        Tests of conversion to an NFA, with comparison between matching as
        implemented in the abstract regular expression data structure and
        matching as implemented in the NFA data structure.
        """
        for r in islice(ares(['a', 'b']), 0, 100):
            for full in (False, True):
                ss = list(strs(['a', 'b'], 5))
                sms_r = set((s, m) for s in ss for m in [r(s, full)])
                r_to_nfa = r.to_nfa()
                sms_r_to_nfa = set((s, m) for s in ss for m in [r_to_nfa(s, full)])
                self.assertEqual(sms_r, sms_r_to_nfa)
