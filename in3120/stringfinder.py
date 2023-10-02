#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Iterator, Dict, Any
from .tokenizer import Tokenizer
from .trie import Trie


class StringFinder:
    """
    Given a trie encoding a dictionary of strings, efficiently finds the subset of strings in the dictionary
    that are also present in a given text buffer. I.e., in a sense computes the "intersection" or "overlap"
    between the dictionary and the text buffer.

    Uses a trie-walk algorithm similar to the Aho-Corasick algorithm with some simplifications and some minor
    NLP extensions. The running time of this algorithm is virtually independent of the size of the dictionary,
    and linear in the length of the buffer we are searching in.

    The tokenizer we use when scanning the input buffer is assumed to be the same as the one that was used
    when adding strings to the trie.
    """

    def __init__(self, trie: Trie, tokenizer: Tokenizer):
        self.__trie = trie
        self.__tokenizer = tokenizer

    def scan(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Scans the given buffer and finds all dictionary entries in the trie that are also present in the
        buffer. We only consider matches that begin and end on token boundaries.

        The matching dictionary entries, if any, are yielded back to the client as dictionaries having the
        keys "match" (str) and "range" (Tuple[int, int]).

        In a serious application we'd add more lookup/evaluation features, e.g., support for prefix matching,
        support for leftmost-longest matching (instead of reporting all matches), and support for lemmatization
        or similar linguistic variations.
        """
        # Initialize a list to store current states.
        current_states = []

        # Iterate over the tokens and their corresponding start and stop positions.
        for token, (start, stop) in (self.__tokenizer).tokens(buffer):
            # Set a base state from the root of the trie tree
            current_states.append((self.__trie, start))

            # Update the current trie in all states, preserve starting position.
            # Also remove states where consumption is not possible
            for trie, s_start in current_states:
                new_trie = trie.consume(token)
                if new_trie is not None:
                    current_states.append((new_trie, s_start))

            # Check if current states are in a final state
            # Find the appropriate slice of the buffer that matches the token. Then tokinize and yield result
            for s, s_start in current_states:
                if s.is_final():
                    matched_string = ' '.join(
                        self.__tokenizer.strings(buffer[s_start:stop]))
                    yield {"match": matched_string, "range": (s_start, stop)}

            # Remove states where consumption of a single space isn't possible.
            new_states = []
            for state in current_states:
                trie, s_start = state
                new_trie = trie.consume(' ')
                if new_trie is not None:
                    new_states.append((new_trie, s_start))

            current_states = new_states
