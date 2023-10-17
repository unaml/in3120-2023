#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestTrie(unittest.TestCase):

    def test_access_nodes(self):
        tokenizer = in3120.SimpleTokenizer()
        root = in3120.Trie()
        root.add(["abba", "ørret", "abb", "abbab", "abbor"], tokenizer)
        self.assertTrue(not root.is_final())
        self.assertIsNone(root.consume("snegle"))
        node = root.consume("ab")
        self.assertTrue(not node.is_final())
        node = node.consume("b")
        self.assertTrue(node.is_final())
        self.assertEqual(node, root.consume("abb"))

    def test_dump_strings(self):
        tokenizer = in3120.SimpleTokenizer()
        root = in3120.Trie()
        root.add(["elle", "eller", "ellen", "hurra   for deg"], tokenizer)
        self.assertListEqual(list(root.strings()), ["elle", "ellen", "eller", "hurra for deg"])
        node = root.consume("el")
        self.assertListEqual(list(node.strings()), ["le", "len", "ler"])

    def test_transitions(self):
        tokenizer = in3120.SimpleTokenizer()
        root = in3120.Trie()
        root.add(["abba", "ørret", "abb", "abbab", "abbor"], tokenizer)
        self.assertListEqual(root.transitions(), ["a", "ø"])
        node = root.consume("abb")
        self.assertListEqual(node.transitions(), ["a", "o"])
        node = node.consume("o")
        self.assertListEqual(node.transitions(), ["r"])
        node = node.consume("r")
        self.assertListEqual(node.transitions(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
