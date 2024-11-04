import math
import mmh3
from nltk import ngrams
from bitarray import bitarray

class BloomFilter:
    def __init__(self, n: int, f: float):
        """
        Creates a Bloom Filter object.

        Args:
            n (int): max number of elements
            f (float): desired false positive rate
        """
        self.n = n
        self.f = f
        self.m = int(-math.log(self.f) * self.n / (math.log(2) ** 2))
        self.k = int(self.m * math.log(2) / self.n)
        self.bit_array = bitarray(self.m)
        self.bit_array.setall(0)

    def add(self, item):
        """Adds an item into the bloom filter.

        Args:
            item (str): Text to be added into the filter.
        """
        tokens = item.lower().split()
        for n in range(1, 4):
            n_grams = ngrams(tokens, n)
            for piece in n_grams:
                for i in range(self.k):
                    index = mmh3.hash(" ".join(piece), i) % self.m
                    self.bit_array[index] = 1

    def query(self, item):
        """Determines if an item is in the filter.

        Args:
            item (str): text to check in the filter.
        """
        tokens = item.lower().split()
        for n in range(1, 4):
            n_grams = ngrams(tokens, n)
            for piece in n_grams:
                for i in range(self.k):
                    index = mmh3.hash(" ".join(piece), i) % self.m
                    if self.bit_array[index] == 0:
                        return False
        return True
