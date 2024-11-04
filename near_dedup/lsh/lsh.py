import hashlib
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Set, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AbstractLSH(ABC):
    @abstractmethod
    def shingle_document(self, doc: str) -> Set[str]:
        pass

    @abstractmethod
    def minhash(self, shingles: Set[str]) -> List[int]:
        pass

    @abstractmethod
    def banding(self, signature: List[int]) -> List[int]:
        pass

    @abstractmethod
    def add_document(self, doc_id: int, doc: str):
        pass

    @abstractmethod
    def find_candidates(self) -> List[Tuple[int, int]]:
        pass


class LSH(AbstractLSH):
    def __init__(
        self, num_bands: int, rows_per_band: int, num_hashes: int, shingle_size: int = 5
    ):
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.num_hashes = num_hashes
        self.shingle_size = shingle_size
        self.buckets = defaultdict(list)
        logging.info(
            f"Initialized LSH with {num_bands} bands, {rows_per_band} rows per band, {num_hashes} hash functions."
        )

    def shingle_document(self, doc: str) -> Set[str]:
        shingles = {
            doc[i : i + self.shingle_size]
            for i in range(len(doc) - self.shingle_size + 1)
        }
        logging.debug(f"Generated {len(shingles)} shingles for document.")
        return shingles

    def minhash(self, shingles: Set[str]) -> List[int]:
        signature = []
        for i in range(self.num_hashes):
            min_hash = float("inf")
            for shingle in shingles:
                hash_value = int(
                    hashlib.md5((str(i) + shingle).encode()).hexdigest(), 16
                )
                min_hash = min(min_hash, hash_value)
            signature.append(min_hash)
        logging.debug(
            f"Computed minhash signature: {signature[:5]}..."
        )  # Show a sample of the signature
        return signature

    def banding(self, signature: List[int]) -> List[int]:
        band_hashes = []
        for band in range(self.num_bands):
            band_signature = signature[
                band * self.rows_per_band : (band + 1) * self.rows_per_band
            ]
            band_hash = int(hashlib.md5(str(band_signature).encode()).hexdigest(), 16)
            band_hashes.append(band_hash)
        logging.debug(
            f"Generated band hashes: {band_hashes[:5]}..."
        )  # Show a sample of the hashes
        return band_hashes

    def add_document(self, doc_id: int, doc: str):
        shingles = self.shingle_document(doc)
        signature = self.minhash(shingles)
        for band_hash in self.banding(signature):
            self.buckets[band_hash].append(doc_id)
        logging.info(f"Document {doc_id} added to LSH.")

    def find_candidates(self):
        candidate_pairs = set()
        for bucket_docs in self.buckets.values():
            for i in range(len(bucket_docs)):
                for j in range(i + 1, len(bucket_docs)):
                    candidate_pairs.add((bucket_docs[i], bucket_docs[j]))
        logging.info(f"Candidate pairs found: {len(candidate_pairs)} pairs")
        return list(candidate_pairs)


class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
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
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0


class LSHWithUnionFind(LSH):
    def __init__(
        self, num_bands: int, rows_per_band: int, num_hashes: int, shingle_size: int = 5
    ):
        super().__init__(num_bands, rows_per_band, num_hashes, shingle_size)
        self.uf = UnionFind()

    def cluster_candidates(self) -> dict:
        candidate_pairs = self.find_candidates()
        for doc1, doc2 in candidate_pairs:
            self.uf.add(doc1)
            self.uf.add(doc2)
            self.uf.union(doc1, doc2)

        clusters = defaultdict(list)
        for doc_id in self.uf.parent:
            root = self.uf.find(doc_id)
            clusters[root].append(doc_id)
        logging.info(f"Clustered {len(clusters)} unique groups from candidates.")
        return clusters
