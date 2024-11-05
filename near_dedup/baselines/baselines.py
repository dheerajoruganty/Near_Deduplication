import hashlib
import logging
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
    """Compute MD5 hash of a document string after cleaning."""
    cleaned_document = (
        document.strip().lower()
    )  # Strip whitespace and convert to lowercase
    hash_value = hashlib.md5(cleaned_document.encode("utf-8")).hexdigest()
    return hash_value


def find_exact_duplicates(documents):
    """Find exact duplicate documents based on MD5 hashing."""
    seen_hashes = {}
    duplicates = []
    logger.info("Starting exact duplicate detection using MD5 hashing.")
    for idx, doc in enumerate(documents):
        md5_hash = compute_md5(doc)
        if md5_hash in seen_hashes:
            duplicates.append((seen_hashes[md5_hash], idx))
            logger.debug(
                f"Duplicate found: Document {idx} is a duplicate of Document {seen_hashes[md5_hash]}."
            )
        else:
            seen_hashes[md5_hash] = idx
    logger.info(
        f"Exact duplicate detection complete. Found {len(duplicates)} duplicate pairs."
    )
    return duplicates


from nltk.tokenize import word_tokenize


def tokenize_ngrams(document, n=3):
    """Tokenize document into n-grams."""
    tokens = document.split()  # Split on whitespace by default
    if len(tokens) < n:
        return []  # Return an empty list if not enough tokens for n-grams
    return list(ngrams(tokens, n))


def find_ngram_duplicates(documents, n=3, threshold=0.8):
    """Find duplicate documents based on n-gram Jaccard similarity.

    Parameters:
        documents (list): List of document strings.
        n (int): N-gram size.
        threshold (float): Threshold for considering documents as duplicates.

    Returns:
        list: List of tuples with duplicate document indices.
    """
    ngram_sets = {}
    duplicates = []
    logger.info("Starting n-gram duplicate detection.")

    for doc_id, doc in enumerate(documents):
        ngrams_list = tokenize_ngrams(doc, n=n)
        ngram_set = set(ngrams_list)

        logger.debug(f"Document {doc_id} has {len(ngram_set)} n-grams.")

        if not ngram_set:
            logger.debug(f"Document {doc_id} skipped: fewer than {n} tokens.")
            continue

        for other_id, other_ngram_set in ngram_sets.items():
            intersection = ngram_set & other_ngram_set
            union = ngram_set | other_ngram_set
            similarity = len(intersection) / len(union) if union else 0

            logger.debug(
                f"Similarity between Document {doc_id} and Document {other_id}: {similarity:.4f}"
            )

            if similarity >= threshold:
                duplicates.append((doc_id, other_id))
                logger.debug(
                    f"N-Gram duplicate found: Document {doc_id} is similar to Document {other_id} with similarity {similarity:.4f}."
                )

        ngram_sets[doc_id] = ngram_set

    logger.info(
        f"N-gram duplicate detection complete. Found {len(duplicates)} duplicate pairs."
    )
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
    """Find duplicate documents based on Jaccard similarity."""
    duplicates = []
    logger.info("Starting Jaccard duplicate detection.")
    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            if jaccard_similarity(documents[i], documents[j]) >= threshold:
                duplicates.append((i, j))
                logger.debug(
                    f"Jaccard duplicate found: Document {i} is similar to Document {j}."
                )
    logger.info(
        f"Jaccard duplicate detection complete. Found {len(duplicates)} duplicate pairs."
    )
    return duplicates


# Baseline 4: Bloom Filter Duplicate Detection
def bloom_filter_duplicates(documents, num_elements=1000, false_positive_rate=0.01):
    """
    Detect duplicates in a document list using Bloom Filter.
    """
    bloom_filter = BloomFilter(num_elements, false_positive_rate)
    duplicates = []
    logger.info("Starting Bloom Filter duplicate detection.")
    for idx, doc in enumerate(documents):
        if bloom_filter.contains(doc):
            duplicates.append(idx)
            logger.debug(f"Bloom Filter duplicate found for Document {idx}.")
        else:
            bloom_filter.add(doc)
    logger.info(
        f"Bloom Filter duplicate detection complete. Found {len(duplicates)} duplicate entries."
    )
    return duplicates


# Baseline 5: LSH Duplicate Detection
def lsh_duplicates(documents, num_bands=10, rows_per_band=5, num_hashes=100):
    """
    Detect duplicates in a document list using LSH.
    """
    lsh = LSH(num_bands, rows_per_band, num_hashes)
    duplicates = []
    logger.info("Starting LSH duplicate detection.")

    # Add each document to the LSH structure
    for idx, doc in enumerate(documents):
        lsh.add_document(idx, doc)

    # Find candidate duplicate pairs
    candidates = lsh.find_candidates()
    for doc1, doc2 in candidates:
        if doc1 != doc2:
            duplicates.append((doc1, doc2))
            logger.debug(
                f"LSH candidate pair found: Document {doc1} and Document {doc2}."
            )

    logger.info(
        f"LSH duplicate detection complete. Found {len(duplicates)} candidate pairs."
    )
    return duplicates
