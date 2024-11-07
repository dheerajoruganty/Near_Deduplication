import hashlib
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Set, Tuple, Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AbstractLSH(ABC):
    """Abstract class for Locality Sensitive Hashing (LSH) operations."""

    @abstractmethod
    def shingle_document(self, doc: str) -> Set[str]:
        """Generates shingles (substrings) from a document."""
        pass

    @abstractmethod
    def minhash(self, shingles: Set[str]) -> List[int]:
        """Generates a minhash signature for a given set of shingles."""
        pass

    @abstractmethod
    def banding(self, signature: List[int]) -> List[int]:
        """Divides a minhash signature into bands and returns band hashes."""
        pass

    @abstractmethod
    def add_document(self, doc_id: int, doc: str):
        """Adds a document to the LSH structure by generating its signature and hashing its bands."""
        pass

    @abstractmethod
    def find_candidates(self) -> List[Tuple[int, int]]:
        """Finds candidate pairs of documents that are likely to be similar."""
        pass


class LSHBase(AbstractLSH):
    """Locality Sensitive Hashing (LSH) for finding near-duplicate documents."""

    def __init__(
        self, num_bands: int, rows_per_band: int, num_hashes: int, shingle_size: int = 5
    ):
        """
        Initializes the LSH with the specified parameters.

        Parameters:
        - num_bands: Number of bands to divide the signature into.
        - rows_per_band: Number of rows per band.
        - num_hashes: Number of hash functions to generate the minhash signature.
        - shingle_size: Size of each shingle (substring) to be generated from documents.
        """
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.num_hashes = num_hashes
        self.shingle_size = shingle_size
        self.buckets = defaultdict(list)
        logging.info(
            f"Initialized LSH with {num_bands} bands, {rows_per_band} rows per band, {num_hashes} hash functions."
        )

    def shingle_document(self, doc: str) -> Set[str]:
        """
        Generates shingles (substrings) of fixed size from the document.

        Parameters:
        - doc: Document as a string.

        Returns:
        - A set of shingles extracted from the document.
        """
        return {
            doc[i : i + self.shingle_size]
            for i in range(len(doc) - self.shingle_size + 1)
        }

    def minhash(self, shingles: Set[str]) -> List[int]:
        """
        Generates a minhash signature from the set of shingles.

        Parameters:
        - shingles: Set of shingles from a document.

        Returns:
        - List of integers representing the minhash signature.
        """
        signature = []
        for i in range(self.num_hashes):
            min_hash = float("inf")
            for shingle in shingles:
                hash_value = int(
                    hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16
                )
                min_hash = min(min_hash, hash_value)
            signature.append(min_hash)
        return signature

    def banding(self, signature: List[int]) -> List[int]:
        """
        Divides the minhash signature into bands and hashes each band.

        Parameters:
        - signature: Minhash signature list.

        Returns:
        - List of integers representing the hash of each band.
        """
        band_hashes = []
        for band in range(self.num_bands):
            band_signature = signature[
                band * self.rows_per_band : (band + 1) * self.rows_per_band
            ]
            band_hash = int(hashlib.md5(str(band_signature).encode()).hexdigest(), 16)
            band_hashes.append(band_hash)
        return band_hashes

    def add_document(self, doc_id: int, doc: str):
        """
        Adds a document to the LSH by hashing its signature bands and storing them in buckets.

        Parameters:
        - doc_id: Unique identifier for the document.
        - doc: Document as a string.
        """
        shingles = self.shingle_document(doc)
        signature = self.minhash(shingles)
        for band_hash in self.banding(signature):
            self.buckets[band_hash].append(doc_id)

    def find_candidates(self):
        """
        Finds pairs of documents that are candidates for being similar.

        Returns:
        - A list of tuples, where each tuple contains two document IDs that are candidate pairs.
        """
        candidate_pairs = set()
        for bucket_docs in self.buckets.values():
            for i in range(len(bucket_docs)):
                for j in range(i + 1, len(bucket_docs)):
                    candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        return list(candidate_pairs)


class UnionFind:
    """Union-Find data structure for clustering similar documents."""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x: int) -> int:
        """
        Finds the root of x with path compression.

        Parameters:
        - x: Element to find.

        Returns:
        - Root of the element.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        """
        Unions the sets containing x and y with rank optimization.

        Parameters:
        - x: First element.
        - y: Second element.
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
        Adds a new element x to the Union-Find structure.

        Parameters:
        - x: Element to add.
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0


class LSH(LSHBase):
    """LSH with Union-Find for clustering similar documents."""

    def __init__(
        self, num_bands: int, rows_per_band: int, num_hashes: int, shingle_size: int = 5
    ):
        super().__init__(num_bands, rows_per_band, num_hashes, shingle_size)
        self.uf = UnionFind()

    def cluster_candidates(self) -> dict:
        """
        Clusters documents based on candidate pairs using Union-Find.

        Returns:
        - A dictionary where each key is a root document ID, and the value is a list of document IDs in that cluster.
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


class LSHImproved:
    """Improved LSH with multi-probe support and Union-Find for clustering."""

    def __init__(
        self,
        num_bands: int,
        rows_per_band: int,
        num_hashes: int,
        shingle_size: int = 5,
        probes: int = 1,
    ):
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.num_hashes = num_hashes
        self.shingle_size = shingle_size
        self.probes = probes
        self.buckets = defaultdict(list)
        self.uf = UnionFind()

    def shingle_document(self, doc: str) -> Set[str]:
        """Generates shingles (substrings) of fixed size from the document."""
        return {
            doc[i : i + self.shingle_size]
            for i in range(len(doc) - self.shingle_size + 1)
        }

    def calculate_probability(self, similarity: float) -> float:
        """Calculate the probability of two items being in the same bucket at least once based on similarity."""
        r = self.rows_per_band
        b = self.num_bands
        return 1 - (1 - similarity**r) ** b

    def minhash(self, shingles: Set[str]) -> List[int]:
        """Generates a minhash signature from the set of shingles."""
        signature = []
        for i in range(self.num_hashes):
            min_hash = float("inf")
            for shingle in shingles:
                hash_value = int(
                    hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16
                )
                min_hash = min(min_hash, hash_value)
            signature.append(min_hash)
        return signature

    def multi_probe_banding(self, signature: List[int]) -> List[int]:
        """Divides the minhash signature into bands and hashes each band with multi-probe support."""
        band_hashes = []
        for band in range(self.num_bands):
            band_signature = signature[
                band * self.rows_per_band : (band + 1) * self.rows_per_band
            ]
            base_band_hash = int(
                hashlib.md5(str(band_signature).encode()).hexdigest(), 16
            )
            band_hashes.append(base_band_hash)
            for probe in range(1, self.probes + 1):
                band_hashes.extend([base_band_hash + probe, base_band_hash - probe])
        return band_hashes

    def add_document(self, doc_id: int, doc: str):
        """Adds a document to the Improved LSH by hashing its signature bands and storing them in buckets."""
        shingles = self.shingle_document(doc)
        signature = self.minhash(shingles)
        for band_hash in self.multi_probe_banding(signature):
            self.buckets[band_hash].append(doc_id)

    def find_candidates(self) -> List[Tuple[int, int]]:
        """Finds candidate pairs of documents that are likely to be similar."""
        candidate_pairs = set()
        for bucket_docs in self.buckets.values():
            for i in range(len(bucket_docs)):
                for j in range(i + 1, len(bucket_docs)):
                    candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        return list(candidate_pairs)

    def cluster_candidates(self) -> Dict[int, List[int]]:
        """Clusters documents based on candidate pairs using Union-Find."""
        candidate_pairs = self.find_candidates()
        for doc1, doc2 in candidate_pairs:
            self.uf.add(doc1)
            self.uf.add(doc2)
            self.uf.union(doc1, doc2)

        # Group clusters by their root document
        clusters = defaultdict(list)
        for doc_id in self.uf.parent:
            root = self.uf.find(doc_id)
            clusters[root].append(doc_id)

        # Sort each cluster for consistent output
        for key in clusters:
            clusters[key].sort()
        return clusters

    def get_clusters(self) -> str:
        """Returns clusters as a formatted string, with each cluster on a new line and document IDs separated by spaces."""
        clusters = self.cluster_candidates()
        formatted_clusters = [
            " ".join(map(str, cluster)) for cluster in clusters.values()
        ]
        return "\n".join(formatted_clusters)
