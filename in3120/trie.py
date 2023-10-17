#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, List, Optional, Iterable, Iterator
from .tokenizer import Tokenizer


class Trie:
    """
    A very simple and straightforward implementation of a trie for demonstration purposes
    and tiny dictionaries.

    A serious real-world implementation of a trie or an automaton would not be implemented
    this way. The trie/automaton would then instead be encoded into a single contiguous buffer
    and there'd be significant attention on memory consumption and scalability with respect to
    dictionary size.

    A node in the trie is also a trie itself in this implementation.
    """

    def __init__(self):
        self.__children: Dict[str, Trie] = {}

    def __repr__(self):
        return repr(self.__children)

    def __add(self, string: str) -> None:
        assert 0 < len(string)
        trie = self
        for symbol in string:
            if symbol not in trie.__children:
                trie.__children[symbol] = Trie()
            trie = trie.__children[symbol]
        trie.__children[""] = Trie()

    def add(self, strings: Iterable[str], tokenizer: Tokenizer) -> None:
        """
        Adds all the strings to the trie. The tokenizer is used so that we're robust
        to nuances in whitespace and punctuation. Use the same tokenizer throughout.
        """
        # TODO: Make the tokenizer a class variable.
        for string in strings:
            self.__add(" ".join(tokenizer.strings(string)))

    def consume(self, prefix: str) -> Optional[Trie]:
        """
        Consumes the given prefix, verbatim. If strings that have this prefix have been added to
        the trie, then the trie node corresponding to the prefix is returned. Otherwise, None is returned.
        """
        node = self
        for symbol in prefix:
            if symbol in node.__children:
                node = node.__children[symbol]
            else:
                return None
        return node

    def strings(self) -> Iterator[str]:
        """
        Yields all strings that are found in or below this node. For simple testing and debugging purposes.
        The returned strings are emitted back in lexicographical order.
        """
        stack = [(self, "")]
        while stack:
            node, prefix = stack.pop()
            if node.is_final():
                yield prefix
            for symbol, child in sorted(node.__children.items(), reverse=True):
                stack.append((child, prefix + symbol))

    def transitions(self) -> List[str]:
        """
        Returns the set of symbols that are valid outgoing transitions, i.e., the set of symbols that
        when consumed by this node would lead to a valid child node. The returned transitions are
        emitted back in lexicographical order.
        """
        return sorted(s for s in self.__children if s)

    def is_final(self) -> bool:
        """
        Returns True iff the current node is a final/terminal state in the trie/automaton, i.e.,
        if a string has been added to the trie where the end of the string ends up in this node.
        """
        return "" in self.__children
