import hashlib
from bitarray import bitarray
import math


class BloomFilter:
    """
    Bloom Filter for approximate membership checking.
    """

    def __init__(self, num_elements: int, false_positive_rate: float = 0.01):
        """
        Initialize the Bloom Filter.

        Parameters:
            num_elements (int): Estimated number of elements to store in the filter.
            false_positive_rate (float): Desired false positive rate.
        """
        self.false_positive_rate = false_positive_rate
        self.size = self.calculate_size(num_elements, false_positive_rate)
        self.num_hashes = self.calculate_hash_count(self.size, num_elements)
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    def calculate_size(self, num_elements: int, false_positive_rate: float) -> int:
        """
        Calculate the size of the bit array.

        Parameters:
            num_elements (int): Number of elements to store.
            false_positive_rate (float): Desired false positive rate.

        Returns:
            int: Size of the bit array.
        """
        return int(-num_elements * math.log(false_positive_rate) / (math.log(2) ** 2))

    def calculate_hash_count(self, size: int, num_elements: int) -> int:
        """
        Calculate the number of hash functions needed.

        Parameters:
            size (int): Size of the bit array.
            num_elements (int): Number of elements to store.

        Returns:
            int: Number of hash functions.
        """
        return int((size / num_elements) * math.log(2))

    def add(self, item: str):
        """
        Add an item to the Bloom Filter.

        Parameters:
            item (str): Item to add.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            self.bit_array[digest] = 1

    def contains(self, item: str) -> bool:
        """
        Check if an item is in the Bloom Filter.

        Parameters:
            item (str): Item to check.

        Returns:
            bool: True if the item might be in the filter, False if it is definitely not.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            if not self.bit_array[digest]:
                return False
        return True
