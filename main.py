import argparse
from near_dedup.deduplicator.deduplicator import DocumentDeduplicator

def main():
    parser = argparse.ArgumentParser(description="Deduplication and Approximate Nearest Neighbor Search using Bloom Filter and LSH")
    
    # Main mode selection
    parser.add_argument("--mode", type=str, choices=["dedup", "search"], required=True,
                        help="Mode of operation: 'dedup' for collection deduplication, 'search' for approximate nearest neighbors.")
    
    # Arguments for deduplication
    parser.add_argument("--documents", type=str, nargs='+', required=True,
                        help="List of document strings for deduplication or indexing. Each document should be a separate string.")
    
    # Argument for nearest neighbor search (only used in search mode)
    parser.add_argument("--query", type=str, help="Query document string for nearest neighbor search.")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the DocumentDeduplicator with desired Bloom Filter and LSH parameters
    deduplicator = DocumentDeduplicator(bloom_filter_params=(1000, 0.01), lsh_params=(10, 5, 100))
    
    # Deduplication Mode
    if args.mode == "dedup":
        # Run deduplication on the provided documents
        exact_duplicates, clusters = deduplicator.deduplicate_collection(args.documents)
        
        # Output the results
        print("Exact Duplicates Removed:")
        for doc in exact_duplicates:
            print(f" - {doc}")
        
        print("\nDocument Clusters (based on near-duplicates):")
        for cluster_id, cluster in enumerate(clusters, 1):
            print(f"Cluster {cluster_id}: {', '.join(str(doc_id) for doc_id in cluster)}")
    
    # Nearest Neighbor Search Mode
    elif args.mode == "search":
        if not args.query:
            parser.error("The --query argument is required for nearest neighbor search mode.")
        
        # Build an index of documents for nearest neighbor search
        deduplicator.build_index(args.documents)
        
        # Perform nearest neighbor search with the query document
        neighbors = deduplicator.nearest_neighbor_search(args.query)
        
        # Output the results
        print("Nearest Neighbors for Query Document:")
        for cluster_id, cluster in neighbors.items():
            print(f"Cluster {cluster_id}: {', '.join(str(doc_id) for doc_id in cluster)}")

if __name__ == "__main__":
    main()
