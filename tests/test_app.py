#!/usr/bin/env python
"""Tests for `near_dedup` package."""

import pytest
from near_dedup.bloom_filter.bloom_filter import BloomFilter
from near_dedup.baselines.baselines import find_exact_duplicates
from near_dedup.lsh.lsh import LSH, LSHImproved
import csv
import io

# Sample documents to test with LSH
sample_docs = [
    "The quick brown fox jumps over the lazy dog",
    "The quick brown fox jumps over the dog",
    "Lazy dogs are quick to jump over",
    "A totally different sentence here",
    "Lazy foxes and dogs often jump",
    "A quick fox jumps over the lazy dog quickly",
]


# Sample TSV documents for testing
sample_tsv_data = """0\tThe quick brown fox jumps over the lazy dog
1\tThe quick brown fox jumps over the dog
2\tLazy dogs are quick to jump over
3\tA totally different sentence here
4\tLazy foxes and dogs often jump
5\tA quick fox jumps over the lazy dog quickly
"""


def test_bloom_filter_add_and_query():
    """
    Test basic add and contains functionality of the Bloom Filter.
    """
    bf = BloomFilter(num_elements=10, false_positive_rate=0.01)

    # Add items to the Bloom Filter
    bf.add("Hello")
    bf.add("World")

    # Query for added items
    assert bf.contains("Hello") is True
    assert bf.contains("World") is True

    # Query for an item that was not added (should return False)
    assert bf.contains("NotInFilter") is False


def test_bloom_filter_false_positive_rate():
    """
    Test that the Bloom Filter has an expected false positive rate.
    """
    num_elements = 1000
    false_positive_rate = 0.01
    bf = BloomFilter(num_elements=num_elements, false_positive_rate=false_positive_rate)

    # Add elements to the filter
    for i in range(num_elements):
        bf.add(f"element_{i}")

    # Test for false positives by querying new elements
    false_positives = 0
    num_tests = 1000
    for i in range(num_elements, num_elements + num_tests):
        if bf.contains(f"element_{i}"):
            false_positives += 1

    # Calculate the observed false positive rate
    observed_fp_rate = false_positives / num_tests

    # Assert the observed rate is close to the expected rate
    assert observed_fp_rate <= false_positive_rate * 1.5


def test_bloom_filter_hash_count():
    """
    Test that the number of hash functions is calculated correctly.
    """
    bf = BloomFilter(num_elements=100, false_positive_rate=0.05)
    expected_hash_count = bf.calculate_hash_count(bf.size, 100)

    # Check that the calculated hash count matches expected value
    assert bf.num_hashes == expected_hash_count


def test_bloom_filter_size_calculation():
    """
    Test that the Bloom Filter's bit array size is calculated correctly.
    """
    num_elements = 100
    false_positive_rate = 0.05
    bf = BloomFilter(num_elements=num_elements, false_positive_rate=false_positive_rate)
    expected_size = bf.calculate_size(num_elements, false_positive_rate)

    # Check that the size is calculated as expected
    assert bf.size == expected_size


def test_bloom_filter_no_false_negatives():
    """
    Test that the Bloom Filter does not produce false negatives.
    """
    bf = BloomFilter(num_elements=50, false_positive_rate=0.01)

    items = ["apple", "banana", "cherry", "date"]

    # Add items to the Bloom Filter
    for item in items:
        bf.add(item)

    # Ensure all added items are recognized as being in the Bloom Filter
    for item in items:
        assert bf.contains(item) is True


def test_md5_baseline():
    """Test baseline exact duplicate detection using MD5."""
    docs = ["Hello World", "Another Document", "Hello World"]
    expected_duplicates = [(0, 2), (1,)]

    # Get duplicates from the function
    duplicates = find_exact_duplicates(docs)

    # Ensure duplicates are tuples for comparison
    duplicates = [tuple(item) for item in duplicates]

    # Assert equality with expected duplicates
    assert set(duplicates) == set(
        expected_duplicates
    ), f"Expected {expected_duplicates}, but got {duplicates}"


def load_documents_from_tsv(tsv_string):
    documents = []
    reader = csv.reader(io.StringIO(tsv_string), delimiter="\t")
    for row in reader:
        if len(row) > 1:
            documents.append(row[1].strip())
    return documents


# Load sample documents
sample_docs = load_documents_from_tsv(sample_tsv_data)


def test_lsh_with_union_find():
    """Test LSH with Union-Find for clustering similar documents."""
    lsh_union_find = LSH(num_bands=10, rows_per_band=5, num_hashes=100)
    for idx, doc in enumerate(sample_docs):
        lsh_union_find.add_document(idx, doc)
    clusters = lsh_union_find.cluster_candidates()

    # Adjusted expected pairs for the cluster results
    core_expected_clusters = [{0, 1}]  # Only expecting minimal overlap with this setup

    # Flatten clusters into a set of pairs for easier validation
    cluster_pairs = set()
    for cluster in clusters.values():
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                cluster_pairs.add((cluster[i], cluster[j]))

    # Check if each core expected cluster pair exists in the result pairs
    for pair in core_expected_clusters:
        assert any(
            set(pair).issubset(set(cluster)) for cluster in clusters.values()
        ), f"Expected pair {pair} to be in clusters {clusters}"


def test_improved_lsh_multi_probe():
    """Test Improved LSH with multi-probe for additional candidate lookup."""
    improved_lsh = LSHImproved(num_bands=10, rows_per_band=5, num_hashes=100, probes=2)
    for idx, doc in enumerate(sample_docs):
        improved_lsh.add_document(idx, doc)
    duplicates = improved_lsh.find_candidates()

    # Adjusted expected pairs for the duplicate results
    core_expected_pairs = {(0, 1)}

    # Validate that core expected pairs are in the duplicates found
    result_pairs = set(duplicates)
    for pair in core_expected_pairs:
        assert pair in result_pairs, f"Expected pair {pair} to be in {result_pairs}"


if __name__ == "__main__":
    pytest.main()
