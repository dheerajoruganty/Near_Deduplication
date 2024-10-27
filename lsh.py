import hashlib
import numpy as np
from collections import defaultdict
from typing import List, Tuple

class LSH:
    """
    Locality Sensitive Hashing (LSH) implementation for near duplicate detection.
    """

    def __init__(self, num_bands: int, rows_per_band: int, num_hashes: int):
        """
        Initialize LSH with the given parameters for banding and minhashing.
        @param num_bands: Number of bands for the LSH
        @param rows_per_band: Number of rows per band
        @param num_hashes: Number of hash functions to use for minhashing
        """
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.num_hashes = num_hashes
        self.buckets = defaultdict(list)

    def shingle_document(self, doc: str, k: int = 5) -> set:
        """
        Create k-shingles for a document.
        @param doc: Document as a string
        @param k: Length of each shingle (default is 5)
        @return: A set of shingles
        """
        return {doc[i:i + k] for i in range(len(doc) - k + 1)}

    def minhash(self, shingles: set) -> List[int]:
        """
        Compute minhash signatures for the shingles.
        @param shingles: Set of shingles
        @return: Minhash signature as a list of integers
        """
        signature = []
        for i in range(self.num_hashes):
            min_hash = float('inf')
            for shingle in shingles:
                hash_value = int(hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16)
                if hash_value < min_hash:
                    min_hash = hash_value
            signature.append(min_hash)
        return signature

    def banding(self, signature: List[int]) -> List[int]:
        """
        Divide the signature into bands and hash each band.
        @param signature: Minhash signature of a document
        @return: A list of hashed band signatures
        """
        band_hashes = []
        for band in range(self.num_bands):
            band_signature = signature[band * self.rows_per_band: (band + 1) * self.rows_per_band]
            band_hash = int(hashlib.md5(str(band_signature).encode()).hexdigest(), 16)
            band_hashes.append(band_hash)
        return band_hashes

    def add_document(self, doc_id: int, doc: str):
        """
        Add document to LSH by computing and storing its banded signature.
        @param doc_id: Document ID
        @param doc: Document content as a string
        """
        shingles = self.shingle_document(doc)
        signature = self.minhash(shingles)
        for band_hash in self.banding(signature):
            self.buckets[band_hash].append(doc_id)

    def find_candidates(self) -> List[Tuple[int, int]]:
        """
        Find candidate pairs by grouping similar documents in the same buckets.
        @return: List of candidate document pairs
        """
        candidate_pairs = set()
        for bucket_docs in self.buckets.values():
            for i in range(len(bucket_docs)):
                for j in range(i + 1, len(bucket_docs)):
                    candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        return list(candidate_pairs)