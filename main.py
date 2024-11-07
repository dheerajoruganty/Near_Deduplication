import csv
import argparse
import logging
import os
from near_dedup.deduplicator.deduplicator import DocumentDeduplicator
from near_dedup.baselines.baselines import (
    find_exact_duplicates,
    find_ngram_duplicates,
    find_jaccard_duplicates,
)
from near_dedup.lsh.lsh import LSH, LSHImproved

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Mapping of dataset filenames to desired sizes
dataset_size_mapping = {
    "five.tsv": "5",
    "hundred.tsv": "100",
    "threehundred.tsv": "300",
    "onek.tsv": "1000",
    "tenk.tsv": "10000",
    "hundredk.tsv": "100000",
}


def load_documents(file_path):
    """
    Load documents from a TSV file, where each line is treated as a separate document.
    """
    documents = []
    with open(file_path, "r") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            if len(row) > 1:
                documents.append(
                    row[1].strip()
                )  # Use the second column for the document text
            elif row:
                documents.append(row[0].strip())
    logging.info(f"Loaded {len(documents)} documents from {file_path}.")
    return documents


def save_results(clusters, output_file):
    """
    Save the deduplication clusters to an output file in the specified format.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as file:
        for cluster in clusters:
            sorted_cluster = sorted(cluster)  # Sort for consistent output
            file.write(" ".join(map(str, sorted_cluster)) + "\n")
    logging.info(f"Results saved to {output_file}.")


def generate_output_filename(input_file, algorithm):
    """
    Generate the output filename based on the input file and algorithm.
    """
    dataset_name = os.path.basename(input_file)
    dataset_size = dataset_size_mapping.get(dataset_name, "unknown")
    output_file = f"results/{dataset_size}-{algorithm}.txt"
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Deduplication using Bloom Filter, LSH, Improved LSH, and Union-Find Enhanced LSH"
    )

    # Main mode selection
    parser.add_argument(
        "--mode",
        type=str,
        choices=[
            "dedup",
            "search",
            "baseline",
            "lsh",
            "improved_lsh",
            "union_find_lsh",
        ],
        required=True,
        help="Mode of operation: 'dedup' for collection deduplication, 'search' for nearest neighbors, 'baseline' to run baselines, 'lsh' for base LSH, 'improved_lsh' for optimized LSH, 'union_find_lsh' for Union-Find enhanced LSH.",
    )

    # Input file containing documents
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="Path to the input file containing documents.",
    )

    # Arguments for nearest neighbor search
    parser.add_argument(
        "--query", type=str, help="Query document string for nearest neighbor search."
    )

    # Baseline selection and parameters
    parser.add_argument(
        "--baseline",
        type=str,
        choices=["md5", "ngram", "jaccard"],
        help="The baseline to run: 'md5', 'ngram', or 'jaccard'",
    )
    parser.add_argument(
        "--n", type=int, default=3, help="N-gram size for n-gram baseline (default: 3)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold for n-gram or Jaccard baseline (default: 0.8)",
    )

    # LSH configuration arguments
    parser.add_argument(
        "--num_bands",
        type=int,
        default=10,
        help="Number of bands for LSH (default: 10)",
    )
    parser.add_argument(
        "--rows_per_band",
        type=int,
        default=5,
        help="Number of rows per band for LSH (default: 5)",
    )
    parser.add_argument(
        "--num_hashes",
        type=int,
        default=100,
        help="Number of hash functions for minhash (default: 100)",
    )
    parser.add_argument(
        "--shingle_size",
        type=int,
        default=5,
        help="Size of each shingle (substring) (default: 5)",
    )
    parser.add_argument(
        "--probes",
        type=int,
        default=1,
        help="Number of additional probes for multi-probe LSH (default: 1)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Load documents from the input file
    documents = load_documents(args.input_file)

    # Generate output filename based on mode and dataset size
    output_file = generate_output_filename(args.input_file, args.mode)

    # Deduplication Mode
    if args.mode == "dedup":
        logging.info("Starting collection deduplication.")
        deduplicator = DocumentDeduplicator(
            bloom_filter_params=(1000, 0.01),
            lsh_params=(args.num_bands, args.rows_per_band, args.num_hashes),
        )
        exact_duplicates, clusters = deduplicator.deduplicate_collection(documents)
        cluster_ids = [[doc_id for doc_id in cluster] for cluster in clusters]
        save_results(cluster_ids, output_file)

    # Baseline Mode
    elif args.mode == "baseline":
        logging.info("Starting baseline deduplication.")
        if args.baseline == "md5":
            duplicates = find_exact_duplicates(documents)
            save_results(duplicates, output_file)
        elif args.baseline == "ngram":
            duplicates = find_ngram_duplicates(
                documents, n=args.n, threshold=args.threshold
            )
            save_results(duplicates, output_file)
        elif args.baseline == "jaccard":
            duplicates = find_jaccard_duplicates(documents, threshold=args.threshold)
            save_results(duplicates, output_file)

    # Improved LSH Mode
    elif args.mode == "improved_lsh":
        logging.info("Starting improved LSH deduplication.")
        improved_lsh = LSHImproved(
            num_bands=args.num_bands,
            rows_per_band=args.rows_per_band,
            num_hashes=args.num_hashes,
            shingle_size=args.shingle_size,
            probes=args.probes,
        )
        for idx, doc in enumerate(documents):
            improved_lsh.add_document(idx, doc)
        clusters = improved_lsh.cluster_candidates()
        formatted_clusters = [cluster for cluster in clusters.values()]
        save_results(formatted_clusters, output_file)

    # Union-Find LSH Mode
    elif args.mode == "lsh":
        logging.info("Starting Union-Find LSH deduplication.")
        union_find_lsh = LSH(
            num_bands=args.num_bands,
            rows_per_band=args.rows_per_band,
            num_hashes=args.num_hashes,
            shingle_size=args.shingle_size,
        )
        for idx, doc in enumerate(documents):
            union_find_lsh.add_document(idx, doc)
        clusters = union_find_lsh.cluster_candidates()
        save_results(clusters.values(), output_file)


if __name__ == "__main__":
    main()
