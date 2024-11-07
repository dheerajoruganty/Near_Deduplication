import hashlib
from bitarray import bitarray
import math


class BloomFilter:
    """
    Standard Bloom Filter for approximate membership checking.
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
        Calculate the size of the bit array for the given parameters.

        Parameters:
            num_elements (int): Number of elements expected to store.
            false_positive_rate (float): Desired false positive rate.

        Returns:
            int: Calculated size of the bit array.
        """
        return int(-num_elements * math.log(false_positive_rate) / (math.log(2) ** 2))

    def calculate_hash_count(self, size: int, num_elements: int) -> int:
        """
        Calculate the optimal number of hash functions needed.

        Parameters:
            size (int): Size of the bit array.
            num_elements (int): Number of elements expected to store.

        Returns:
            int: Number of hash functions.
        """
        return int((size / num_elements) * math.log(2))

    def add(self, item: str):
        """
        Add an item to the Bloom Filter.

        Parameters:
            item (str): Item to be added.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            self.bit_array[digest] = 1

    def contains(self, item: str) -> bool:
        """
        Check if an item might be in the Bloom Filter.

        Parameters:
            item (str): Item to be checked.

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


class CountingBloomFilter(BloomFilter):
    """
    Counting Bloom Filter for approximate membership checking with support for deletions.
    Each counter is represented by a fixed number of bits within the bitarray.
    """

    def __init__(
        self,
        num_elements: int,
        false_positive_rate: float = 0.01,
        bits_per_counter: int = 4,
    ):
        """
        Initialize the Counting Bloom Filter.

        Parameters:
            num_elements (int): Estimated number of elements to store in the filter.
            false_positive_rate (float): Desired false positive rate.
            bits_per_counter (int): Number of bits used per counter, allowing counts up to 2^bits_per_counter - 1.
        """
        super().__init__(num_elements, false_positive_rate)
        self.bits_per_counter = bits_per_counter
        self.max_count = (1 << bits_per_counter) - 1  # Maximum value for each counter

        # Override bit_array with enough space for `size` counters of `bits_per_counter` bits each
        self.bit_array = bitarray(self.size * bits_per_counter)
        self.bit_array.setall(0)

    def get_counter_value(self, index: int) -> int:
        """
        Retrieve the current count value at the specified index.

        Parameters:
            index (int): Position of the counter.

        Returns:
            int: The count at the specified index.
        """
        start = index * self.bits_per_counter
        end = start + self.bits_per_counter
        return int(self.bit_array[start:end].to01(), 2)

    def set_counter_value(self, index: int, value: int):
        """
        Set the count value at the specified index.

        Parameters:
            index (int): Position of the counter.
            value (int): Value to set, constrained by max_count.
        """
        binary_value = bin(value)[2:].zfill(self.bits_per_counter)
        start = index * self.bits_per_counter
        self.bit_array[start : start + self.bits_per_counter] = bitarray(binary_value)

    def add(self, item: str):
        """
        Add an item to the Counting Bloom Filter by incrementing its counters.

        Parameters:
            item (str): Item to be added.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            current_value = self.get_counter_value(digest)
            if current_value < self.max_count:
                self.set_counter_value(digest, current_value + 1)

    def remove(self, item: str):
        """
        Remove an item from the Counting Bloom Filter by decrementing its counters.

        Parameters:
            item (str): Item to be removed.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            current_value = self.get_counter_value(digest)
            if current_value > 0:
                self.set_counter_value(digest, current_value - 1)

    def contains(self, item: str) -> bool:
        """
        Check if an item might be in the Counting Bloom Filter.

        Parameters:
            item (str): Item to be checked.

        Returns:
            bool: True if all related counters are non-zero, suggesting the item might be in the filter.
        """
        for i in range(self.num_hashes):
            digest = (
                int(hashlib.md5((str(i) + item).encode()).hexdigest(), 16) % self.size
            )
            if self.get_counter_value(digest) == 0:
                return False
        return True
