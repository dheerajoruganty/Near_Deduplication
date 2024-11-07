import hashlib
import logging
from collections import defaultdict
from collections import Counter
from nltk.util import ngrams
from near_dedup.bloom_filter.bloom_filter import BloomFilter
from nltk.tokenize import word_tokenize
import nltk

nltk.download("punkt_tab")

# Configure logging
logger = logging.getLogger(__name__)


# Baseline 1: Exact Duplicate Detection Using MD5 Hashing
def compute_md5(document):
    """Compute MD5 hash of an entire document string after cleaning."""
    cleaned_document = (
        document.strip().lower()
    )  # Strip whitespace and convert to lowercase
    hash_value = hashlib.md5(cleaned_document.encode("utf-8")).hexdigest()
    return hash_value


def find_exact_duplicates(documents):
    """Find clusters of documents based on MD5 hashing."""
    seen_hashes = {}
    logger.info("Starting exact duplicate detection using MD5 hashing.")

    # Create clusters based on exact document content
    for idx, doc in enumerate(documents):
        md5_hash = compute_md5(doc)
        if md5_hash in seen_hashes:
            # Add this document ID to the existing cluster
            seen_hashes[md5_hash].append(idx)
        else:
            # Initialize a new cluster for this unique content
            seen_hashes[md5_hash] = [idx]

    # Return all clusters, including those with single entries
    clusters = list(seen_hashes.values())

    duplicate_cluster_count = sum(
        1 for cluster in seen_hashes.values() if len(cluster) > 1
    )

    logger.info(
        f"Exact duplicate clustering complete. Found {duplicate_cluster_count} clusters with duplicates."
    )
    return clusters


def tokenize_ngrams(document, n=3):
    """Tokenize document into n-grams."""
    tokens = document.split()  # Split on whitespace by default
    if len(tokens) < n:
        return []  # Return an empty list if not enough tokens for n-grams
    return list(ngrams(tokens, n))


def find_ngram_duplicates(documents, n=3, threshold=0.8):
    """Cluster documents based on n-gram Jaccard similarity."""
    ngram_sets = {}
    clusters = defaultdict(list)
    logger.info("Starting n-gram duplicate detection.")

    # Create n-gram sets for each document
    for doc_id, doc in enumerate(documents):
        ngrams_list = tokenize_ngrams(doc, n=n)
        ngram_set = set(ngrams_list)

        if not ngram_set:
            logger.debug(f"Document {doc_id} skipped: fewer than {n} tokens.")
            continue

        # Compare with previous documents
        matched = False
        for other_id, other_ngram_set in ngram_sets.items():
            intersection = ngram_set & other_ngram_set
            union = ngram_set | other_ngram_set
            similarity = len(intersection) / len(union) if union else 0

            if similarity >= threshold:
                clusters[other_id].append(doc_id)
                matched = True
                break

        if not matched:
            clusters[doc_id].append(
                doc_id
            )  # Start a new cluster for this unique document

        ngram_sets[doc_id] = ngram_set

    # Return clusters as a list of lists
    return list(clusters.values())


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
    """Cluster documents based on Jaccard similarity."""
    clusters = defaultdict(list)
    logger.info("Starting Jaccard duplicate detection.")

    for i, doc1 in enumerate(documents):
        matched = False
        for cluster_id, cluster_docs in clusters.items():
            if jaccard_similarity(doc1, documents[cluster_id]) >= threshold:
                cluster_docs.append(i)
                matched = True
                break

        if not matched:
            clusters[i].append(i)  # Start a new cluster if no match found

    # Return clusters as a list of lists
    return list(clusters.values())
