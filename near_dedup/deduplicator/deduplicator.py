from near_dedup.baselines.baselines import compute_md5, find_exact_duplicates, find_ngram_duplicates, find_jaccard_duplicates
from near_dedup.bloom_filter.bloom_filter import BloomFilter
from near_dedup.lsh.lsh import LSH
from collections import defaultdict
import hashlib
import re

class DocumentDeduplicator:
    """
    Class to handle deduplication and approximate nearest neighbor search on a collection of documents.
    """

    def __init__(self, bloom_filter_params=(1000, 0.01), lsh_params=(10, 5, 100)):
        """
        Initialize DocumentDeduplicator with Bloom Filter and LSH parameters.

        Parameters:
            bloom_filter_params (tuple): Parameters for initializing the Bloom Filter.
            lsh_params (tuple): Parameters for initializing LSH (num_bands, rows_per_band, num_hashes).
        """
        self.bloom_filter = BloomFilter(*bloom_filter_params)
        self.lsh = LSH(*lsh_params)
        self.union_set = {}  # For Union-Find

    # Step 1: Remove exact duplicates using Bloom Filter and MD5 hashing
    def remove_exact_duplicates(self, documents):
        unique_docs = []
        duplicates = []

        for doc in documents:
            md5_hash = compute_md5(doc)
            if self.bloom_filter.contains(md5_hash):
                duplicates.append(doc)
            else:
                self.bloom_filter.add(md5_hash)
                unique_docs.append(doc)
                
        return unique_docs, duplicates

    # Step 2: Clean and normalize documents
    def clean_document(self, doc):
        """Normalize document by converting to lowercase and removing punctuation."""
        doc = doc.lower()
        doc = re.sub(r'[^\w\s]', '', doc)  # Remove punctuation
        return doc

    def preprocess_documents(self, documents):
        """Apply cleaning to a list of documents."""
        return [self.clean_document(doc) for doc in documents]

    # Step 3: Compute minhash signatures and Step 4: Find candidate pairs with LSH
    def compute_minhash_and_candidates(self, documents):
        doc_signatures = {}
        for idx, doc in enumerate(documents):
            self.lsh.add_document(idx, doc)  # This will handle both minhash and LSH banding
            doc_signatures[idx] = self.lsh.minhash(self.lsh.shingle_document(doc))
        
        candidate_pairs = self.lsh.find_candidates()
        return doc_signatures, candidate_pairs

    # Step 5: Cluster documents using Union-Find with path compression and union by rank
    def find(self, x):
        """Union-Find 'find' function with path compression."""
        if x != self.union_set.setdefault(x, x):
            self.union_set[x] = self.find(self.union_set[x])  # Path compression
        return self.union_set[x]

    def union(self, x, y):
        """Union-Find 'union' function with union by rank."""
        root_x, root_y = self.find(x), self.find(y)
        if root_x != root_y:
            if root_x < root_y:
                self.union_set[root_y] = root_x
            else:
                self.union_set[root_x] = root_y

    def cluster_documents(self, candidate_pairs):
        """Cluster documents based on candidate pairs using Union-Find."""
        for doc1, doc2 in candidate_pairs:
            self.union(doc1, doc2)
        
        clusters = defaultdict(list)
        for doc_id in self.union_set:
            root = self.find(doc_id)
            clusters[root].append(doc_id)
        return clusters

    # Step 6: Compute Jaccard similarity within clusters
    def compute_jaccard_similarity(self, clusters, doc_signatures):
        """Refine clusters by computing Jaccard similarity between document pairs."""
        refined_clusters = []
        for root, docs in clusters.items():
            cluster = []
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    doc1, doc2 = docs[i], docs[j]
                    jaccard_score = self.jaccard_similarity(doc_signatures[doc1], doc_signatures[doc2])
                    if jaccard_score > 0.7:  # Threshold for similarity
                        cluster.extend([doc1, doc2])
            refined_clusters.append(set(cluster))
        return refined_clusters

    def jaccard_similarity(self, sig1, sig2):
        """Compute Jaccard similarity between two sets of minhash signatures."""
        intersection = len(set(sig1) & set(sig2))
        union = len(set(sig1) | set(sig2))
        return intersection / union if union != 0 else 0

    # Full workflow for collection deduplication
    def deduplicate_collection(self, documents):
        """Perform full deduplication workflow on a collection of documents."""
        # Remove exact duplicates
        unique_docs, exact_duplicates = self.remove_exact_duplicates(documents)

        # Clean and preprocess documents
        cleaned_docs = self.preprocess_documents(unique_docs)

        # Minhash and LSH for candidate pairs
        doc_signatures, candidate_pairs = self.compute_minhash_and_candidates(cleaned_docs)

        # Cluster candidate pairs
        clusters = self.cluster_documents(candidate_pairs)

        # Compute Jaccard similarity within clusters
        refined_clusters = self.compute_jaccard_similarity(clusters, doc_signatures)

        return exact_duplicates, refined_clusters

    # Offline (Indexing) for Nearest Neighbor Search
    def build_index(self, documents):
        """Create an index of minhash signatures for approximate nearest neighbor search."""
        unique_docs, _ = self.remove_exact_duplicates(documents)
        cleaned_docs = self.preprocess_documents(unique_docs)
        index = {}

        for idx, doc in enumerate(cleaned_docs):
            signature = self.lsh.minhash(self.lsh.shingle_document(doc))
            index[idx] = signature

        self.index = index
        return index

    # Online (Querying) for Nearest Neighbor Search
    def nearest_neighbor_search(self, query_doc, threshold=0.7):
        """Find approximate nearest neighbors for a query document."""
        cleaned_query = self.clean_document(query_doc)
        query_signature = self.lsh.minhash(self.lsh.shingle_document(cleaned_query))
        
        # Find candidates using LSH
        candidates = []
        for idx, signature in self.index.items():
            if self.jaccard_similarity(query_signature, signature) > threshold:
                candidates.append(idx)
        
        # Cluster the candidates with Union-Find
        clusters = self.cluster_documents([(0, c) for c in candidates])  # Single document to candidates
        
        return clusters
