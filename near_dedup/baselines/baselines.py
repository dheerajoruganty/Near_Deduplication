import hashlib
from collections import Counter
from nltk.util import ngrams
from near_dedup.bloom_filter.bloom_filter import BloomFilter
from near_dedup.lsh.lsh import LSH


# Baseline 1: Exact Duplicate Detection Using MD5 Hashing
def compute_md5(document):
    """Compute MD5 hash of a document string."""
    return hashlib.md5(document.encode("utf-8")).hexdigest()


def find_exact_duplicates(documents):
    """Find exact duplicate documents based on MD5 hashing.

    Parameters:
        documents (list): List of document strings.

    Returns:
        list: List of tuples with duplicate document indices.
    """
    seen_hashes = {}
    duplicates = []
    for idx, doc in enumerate(documents):
        md5_hash = compute_md5(doc)
        if md5_hash in seen_hashes:
            duplicates.append((seen_hashes[md5_hash], idx))
        else:
            seen_hashes[md5_hash] = idx
    return duplicates


# Baseline 2: N-Gram Matching
def tokenize_ngrams(document, n=3):
    """Tokenize document into n-grams."""
    tokens = document.split()
    return list(ngrams(tokens, n))


def find_ngram_duplicates(documents, n=3, threshold=0.8):
    """Find duplicate documents based on n-gram similarity.

    Parameters:
        documents (list): List of document strings.
        n (int): N-gram size.
        threshold (float): Threshold for considering documents as duplicates.

    Returns:
        list: List of tuples with duplicate document indices.
    """
    ngram_counts = {}
    duplicates = []
    for doc_id, doc in enumerate(documents):
        ngrams_list = tokenize_ngrams(doc, n=n)
        ngram_counter = Counter(ngrams_list)

        # Compare this document's n-grams with others
        for other_id, other_counter in ngram_counts.items():
            common_ngrams = sum((ngram_counter & other_counter).values())
            total_ngrams = sum(ngram_counter.values())
            if common_ngrams / total_ngrams >= threshold:
                duplicates.append((doc_id, other_id))

        ngram_counts[doc_id] = ngram_counter
    return duplicates


# Baseline 3: Jaccard Similarity
def tokenize_words(document):
    """Tokenize document into a set of unique words."""
    return set(document.split())


def jaccard_similarity(doc1, doc2):
    """Compute Jaccard similarity between two sets of words."""
    set1, set2 = tokenize_words(doc1), tokenize_words(doc2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0


def find_jaccard_duplicates(documents, threshold=0.7):
    """Find duplicate documents based on Jaccard similarity.

    Parameters:
        documents (list): List of document strings.
        threshold (float): Threshold for considering documents as duplicates.

    Returns:
        list: List of tuples with duplicate document indices.
    """
    duplicates = []
    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            if jaccard_similarity(documents[i], documents[j]) >= threshold:
                duplicates.append((i, j))
    return duplicates


# Baseline 4: Bloom Filter Duplicate Detection
def bloom_filter_duplicates(documents, num_elements=1000, false_positive_rate=0.01):
    """
    Detect duplicates in a document list using Bloom Filter.
    
    Parameters:
        documents (list): List of document strings.
        num_elements (int): Estimated number of elements to store in the filter.
        false_positive_rate (float): Desired false positive rate.
    
    Returns:
        list: List of document indices suspected of being duplicates.
    """
    bloom_filter = BloomFilter(num_elements, false_positive_rate)
    duplicates = []

    for idx, doc in enumerate(documents):
        if bloom_filter.contains(doc):
            duplicates.append(idx)
        else:
            bloom_filter.add(doc)
    return duplicates


# Baseline 5: LSH Duplicate Detection
def lsh_duplicates(documents, num_bands=10, rows_per_band=5, num_hashes=100):
    """
    Detect duplicates in a document list using LSH.
    
    Parameters:
        documents (list): List of document strings.
        num_bands (int): Number of bands for the LSH.
        rows_per_band (int): Number of rows per band.
        num_hashes (int): Number of hash functions for minhashing.
    
    Returns:
        list: List of tuples with duplicate document indices.
    """
    lsh = LSH(num_bands, rows_per_band, num_hashes)
    duplicates = []

    # Add each document to the LSH structure
    for idx, doc in enumerate(documents):
        lsh.add_document(idx, doc)

    # Find candidate duplicate pairs
    candidates = lsh.find_candidates()

    # Filter out exact duplicates within candidate pairs (optional)
    for doc1, doc2 in candidates:
        if doc1 != doc2:
            duplicates.append((doc1, doc2))

    return duplicates
