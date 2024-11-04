import hashlib
import numpy as np
from collections import defaultdict
from typing import List, Tuple

class LSH:
    """
    Locality Sensitive Hashing (LSH) implementation for near-duplicate detection.
    """

    def __init__(self, num_bands: int, rows_per_band: int, num_hashes: int):
        """
        Initialize LSH with the given parameters for banding and minhashing.
        
        Parameters:
            num_bands (int): Number of bands for the LSH.
            rows_per_band (int): Number of rows per band.
            num_hashes (int): Number of hash functions to use for minhashing.
        """
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.num_hashes = num_hashes
        self.buckets = defaultdict(list)

    def shingle_document(self, doc: str, k: int = 5) -> set:
        """
        Create k-shingles for a document.
        
        Parameters:
            doc (str): Document content as a string.
            k (int): Length of each shingle (default is 5).
        
        Returns:
            set: A set of shingles.
        """
        return {doc[i:i + k] for i in range(len(doc) - k + 1)}

    def minhash(self, shingles: set) -> List[int]:
        """
        Compute minhash signature for the given set of shingles.
        
        Parameters:
            shingles (set): Set of shingles.
        
        Returns:
            List[int]: Minhash signature as a list of integers.
        """
        signature = []
        for i in range(self.num_hashes):
            min_hash = float('inf')
            for shingle in shingles:
                hash_value = int(hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16)
                min_hash = min(min_hash, hash_value)
            signature.append(min_hash)
        return signature

    def banding(self, signature: List[int]) -> List[int]:
        """
        Divide the signature into bands and hash each band.
        
        Parameters:
            signature (List[int]): Minhash signature of a document.
        
        Returns:
            List[int]: A list of hashed band signatures.
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
        
        Parameters:
            doc_id (int): Document ID.
            doc (str): Document content as a string.
        """
        shingles = self.shingle_document(doc)
        signature = self.minhash(shingles)
        for band_hash in self.banding(signature):
            self.buckets[band_hash].append(doc_id)

    def find_candidates(self) -> List[Tuple[int, int]]:
        """
        Find candidate pairs by grouping similar documents in the same buckets.
        
        Returns:
            List[Tuple[int, int]]: List of candidate document pairs (doc_id1, doc_id2).
        """
        candidate_pairs = set()
        for bucket_docs in self.buckets.values():
            for i in range(len(bucket_docs)):
                for j in range(i + 1, len(bucket_docs)):
                    candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        return list(candidate_pairs)


class UnionFind:
    """
    Union-Find data structure to support clustering of similar documents.
    """

    def __init__(self):
        """
        Initialize the Union-Find data structure.
        """
        self.parent = {}
        self.rank = {}

    def find(self, x: int) -> int:
        """
        Find the root of x with path compression.
        
        Parameters:
            x (int): Element to find.
        
        Returns:
            int: Root of x.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        """
        Union by rank to merge two sets containing x and y.
        
        Parameters:
            x (int): First element.
            y (int): Second element.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

    def add(self, x: int):
        """
        Add a new element to the Union-Find structure.
        
        Parameters:
            x (int): Element to add.
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0


class LSHWithUnionFind(LSH):
    """
    Extended LSH with Union-Find for clustering.
    """

    def __init__(self, num_bands: int, rows_per_band: int, num_hashes: int):
        """
        Initialize the extended LSH with Union-Find for clustering.
        
        Parameters:
            num_bands (int): Number of bands for the LSH.
            rows_per_band (int): Number of rows per band.
            num_hashes (int): Number of hash functions for minhashing.
        """
        super().__init__(num_bands, rows_per_band, num_hashes)
        self.uf = UnionFind()

    def cluster_candidates(self) -> dict:
        """
        Cluster candidate pairs using Union-Find to deduplicate documents.
        
        Returns:
            dict: Dictionary where keys are cluster roots and values are lists of document IDs in the cluster.
        """
        candidate_pairs = self.find_candidates()
        for doc1, doc2 in candidate_pairs:
            self.uf.add(doc1)
            self.uf.add(doc2)
            self.uf.union(doc1, doc2)

        clusters = defaultdict(list)
        for doc_id in self.uf.parent:
            root = self.uf.find(doc_id)
            clusters[root].append(doc_id)
        return clusters


class LSHImproved(LSHWithUnionFind):
    """
    Extended LSH with improvements like Universal Hashing and Multi-probe LSH.
    """

    def universal_hashing(self, shingle: str) -> int:
        """
        Universal hashing function using SHA-256.
        
        Parameters:
            shingle (str): Shingle to hash.
        
        Returns:
            int: Hashed value using SHA-256.
        """
        return int(hashlib.sha256(shingle.encode()).hexdigest(), 16)

    def multi_probe_banding(self, signature: List[int], probes: int = 1) -> List[int]:
        """
        Multi-probe LSH to explore neighboring buckets by probing for similar signatures.
        
        Parameters:
            signature (List[int]): Minhash signature of a document.
            probes (int): Number of additional probes to perform for neighboring buckets (default is 1).
        
        Returns:
            List[int]: List of hash values for bands including additional probe hashes.
        """
        band_hashes = super().banding(signature)
        probe_hashes = []
        for band_hash in band_hashes:
            probe_hashes.append(band_hash)
            for probe in range(1, probes + 1):
                probe_hashes.append(band_hash + probe)
                probe_hashes.append(band_hash - probe)
        return probe_hashes
