import csv
import argparse
import logging
from near_dedup.deduplicator.deduplicator import DocumentDeduplicator
from near_dedup.baselines.baselines import (
    find_exact_duplicates,
    find_ngram_duplicates,
    find_jaccard_duplicates,
    bloom_filter_duplicates,
    lsh_duplicates,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
    with open(output_file, "w") as file:
        for cluster in clusters:
            file.write(" ".join(map(str, cluster)) + "\n")
    logging.info(f"Results saved to {output_file}.")


def main():
    parser = argparse.ArgumentParser(
        description="Deduplication using Bloom Filter, LSH, and Baseline Methods"
    )

    # Main mode selection
    parser.add_argument(
        "--mode",
        type=str,
        choices=["dedup", "search", "baseline"],
        required=True,
        help="Mode of operation: 'dedup' for collection deduplication, 'search' for nearest neighbors, 'baseline' to run baselines.",
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
        choices=["md5", "ngram", "jaccard", "bloom", "lsh"],
        help="The baseline to run: 'md5', 'ngram', 'jaccard', 'bloom', or 'lsh'.",
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

    # Parse arguments
    args = parser.parse_args()

    # Load documents from the input file
    documents = load_documents(args.input_file)

    # Initialize the DocumentDeduplicator with desired Bloom Filter and LSH parameters
    deduplicator = DocumentDeduplicator(
        bloom_filter_params=(1000, 0.01), lsh_params=(10, 5, 100)
    )

    # Deduplication Mode
    if args.mode == "dedup":
        logging.info("Starting collection deduplication.")
        exact_duplicates, clusters = deduplicator.deduplicate_collection(documents)
        cluster_ids = [[doc_id for doc_id in cluster] for cluster in clusters]
        output_file = f"{args.input_file.split('.')[0]}-lsh.txt"
        save_results(cluster_ids, output_file)

    # Nearest Neighbor Search Mode
    elif args.mode == "search":
        if not args.query:
            parser.error(
                "The --query argument is required for nearest neighbor search mode."
            )
        logging.info("Building index for nearest neighbor search.")
        deduplicator.build_index(documents)
        neighbors = deduplicator.nearest_neighbor_search(args.query)
        print("Nearest Neighbors for Query Document:")
        for cluster_id, cluster in neighbors.items():
            print(
                f"Cluster {cluster_id}: {', '.join(str(doc_id) for doc_id in cluster)}"
            )

    # Baseline Mode
    elif args.mode == "baseline":
        if not args.baseline:
            parser.error("The --baseline argument is required for baseline mode.")

        # Run each baseline based on the provided argument
        if args.baseline == "md5":
            duplicates = find_exact_duplicates(documents)
            print("Exact Duplicates Found (MD5):")
            for doc1, doc2 in duplicates:
                print(f"Document {doc1} is a duplicate of Document {doc2}")

        elif args.baseline == "ngram":
            duplicates = find_ngram_duplicates(
                documents, n=args.n, threshold=args.threshold
            )
            print("Near-Duplicates Found (N-Gram):")
            for doc1, doc2 in duplicates:
                print(f"Document {doc1} is similar to Document {doc2} (N-Gram)")

        elif args.baseline == "jaccard":
            duplicates = find_jaccard_duplicates(documents, threshold=args.threshold)
            print("Near-Duplicates Found (Jaccard):")
            for doc1, doc2 in duplicates:
                print(f"Document {doc1} is similar to Document {doc2} (Jaccard)")

        elif args.baseline == "bloom":
            duplicates = bloom_filter_duplicates(documents)
            print("Potential Duplicates Found (Bloom Filter):")
            for doc_id in duplicates:
                print(f"Document {doc_id} is a suspected duplicate.")

        elif args.baseline == "lsh":
            duplicates = lsh_duplicates(documents)
            print("Potential Near-Duplicates Found (LSH):")
            for doc1, doc2 in duplicates:
                print(f"Document {doc1} is similar to Document {doc2} (LSH)")


if __name__ == "__main__":
    main()
