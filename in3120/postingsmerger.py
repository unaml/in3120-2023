#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Iterator
from .posting import Posting


class PostingsMerger:
    """
    Utility class for merging posting lists.

    It is currently left unspecified what to do with the term frequency field
    in the returned postings when document identifiers overlap. Different
    approaches are possible, e.g., an arbitrary one of the two postings could
    be returned, or the posting having the smallest/largest term frequency, or
    a new one that produces an averaged value, or something else.
    """

    @staticmethod
    def intersection(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple AND of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        posting1 = next(p1, None)
        posting2 = next(p2, None)

        while posting1 is not None and posting2 is not None:
            if posting1.document_id == posting2.document_id:
                yield posting1
                posting1 = next(p1, None)
                posting2 = next(p2, None)
            elif posting1.document_id < posting2.document_id:
                posting1 = next(p1, None)
            elif posting2.document_id < posting1.document_id:
                posting2 = next(p2, None)

    @staticmethod
    def union(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple OR of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        posting1 = next(p1, None)
        posting2 = next(p2, None)

        while posting1 is not None and posting2 is not None:
            if posting1.document_id == posting2.document_id:
                yield posting1
                posting1 = next(p1, None)
                posting2 = next(p2, None)
            elif posting1.document_id < posting2.document_id:
                yield posting1
                posting1 = next(p1, None)
            elif posting2.document_id < posting1.document_id:
                yield posting2
                posting2 = next(p2, None)

        while posting1 is not None:
            yield posting1
            posting1 = next(p1, None)

        while posting2 is not None:
            yield posting2
            posting2 = next(p2, None)
