import math
import mmh3
import ngram
from nltk import ngrams
from bitarray import bitarray

class BloomFilter:
    def __init__(self, n: int, f: float):
        """
        Creates a Bloom Filter object.

        Args:
            n (int): max number of elements
            f (int): desired false positive rate
        """
        self.n = n
        self.f = f
        self.m = int(-math.log(self.f) * self.n/(math.log(2)**2))
        self.k = int(self.m * math.log(2)/self.n)
        #self.k = 8
        #number of bytes required to store size max number of elements
        self.m_bytes = (self.m + 7) // 8
        self.bit_array = bitarray(self.m)
        self.bit_array.setall(0)
        #self.bit_vector = bytearray(([0] * self.n_bytes))
        #print(len(self.bit_vector))
        #for counting bloom filter
        #self.bits = [0] * self.m
        
        
        
    def add(self,item):
        """Adds an item into the bloom filter.

        Args:
            item (str): Text to be added into the filter.
        """
        for i in range(self.k):
            tokens = item.lower().split()
            
            for n in range(1,4):
                n_grams = ngrams(tokens, n)
                
                for piece in n_grams:
                    
                    index = mmh3.hash(" ".join(piece), i) % self.m 
                    #commented out code is the byte array implementation. 
                    #kept it in because I was trying out both and switching between them.
                    #byte_index, bit_index = divmod(index, 8) #returns q, r
                    #print(byte_index)
                    #print(bit_index)
                    #mask = 1 << bit_index
                    #print(len(self.bit_vector))
                    #self.bit_vector[byte_index] |= mask
                    
                    self.bit_array[index] = 1
                    #for counting bloom filter
                    #self.bits[index] += 1
            
            
            
    def query(self,item):
        """Determines if an item is able to be found. 
        Returns True if the item is in the filter.
        Returns False if the item is not in the filter.

        Args:
            item (str): text intended to see if it is in the filter.
        """
        for i in range(self.k):
            tokens = item.lower().split()
            for n in range(1,4):
                n_grams = ngrams(tokens, n)
                for piece in n_grams:
                    index = mmh3.hash(" ".join(piece), i) % self.m
                    #commented out code is the byte array implementation
                    #kept it in because I was trying out both and switching between them.
                    #byte_index, bit_index = divmod(index, 8) #returns q, r
                    #mask = 1 << bit_index
                    #if (self.bit_vector[byte_index] & mask) == 0:
                    #    return False
                    if self.bit_array[index] == 0:
                        return False
                return True
            
    def remove(self, item):
        for i in range(self.k):
            
            tokens = item.lower().split()
            for n in range(1,4):
                n_grams = ngrams(tokens, n)
                for piece in n_grams:
                    index = mmh3.hash(" ".join(piece), i) % self.m
                    
                    if self.bit_array[index] > 0:
                        self.bit_array[index] -= 1
                
