#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from abc import ABC, abstractmethod
from typing import Iterator, Tuple


class Tokenizer(ABC):
    """
    Simple abstract base class for tokenizers, with some default implementations.
    """

    @abstractmethod
    def ranges(self, buffer: str) -> Iterator[Tuple[int, int]]:
        """
        Returns the positional range pairs that indicate where in the buffer the
        tokens begin and end.
        """
        pass

    def strings(self, buffer: str) -> Iterator[str]:
        """
        Returns the strings that make up the tokens in the given buffer.
        """
        return (buffer[r[0]:r[1]] for r in self.ranges(buffer))

    def tokens(self, buffer: str) -> Iterator[Tuple[str, Tuple[int, int]]]:
        """
        Returns the (string, range) pairs that make up the tokens in the given buffer.
        """
        return ((buffer[r[0]:r[1]], r) for r in self.ranges(buffer))

    def join(self, tokens: Iterator[Tuple[str, Tuple[int, int]]]) -> str:
        """
        General utility method. The inverse of tokens/2, basically: Joins the tokens
        back into a reconstructed buffer, taking care of spaces (or not) between tokens.
        Currently assumes that the provided tokens are sorted in left-to-right order.
        """
        fragments = []
        previous_end = -1
        for (token, (begin, end)) in tokens:
            is_connected, previous_end = (previous_end > 0) and (begin == previous_end), end
            if fragments and not is_connected:
                fragments.append(" ")
            fragments.append(token)
        return "".join(fragments)


class SimpleTokenizer(Tokenizer):
    """
    A dead simple tokenizer for testing purposes. A real tokenizer
    wouldn't be implemented this way.
    """

    # Kids, don't do this at home.
    __pattern = re.compile(r"(\w+)", re.UNICODE | re.MULTILINE | re.DOTALL)

    def __init__(self):
        pass

    def ranges(self, buffer: str) -> Iterator[Tuple[int, int]]:
        return ((m.start(), m.end()) for m in self.__pattern.finditer(buffer))
