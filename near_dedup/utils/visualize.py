import matplotlib.pyplot as plt
import numpy as np


def plot_false_positive_rate_vs_hash_functions(num_hashes, false_positive_rates):
    plt.plot(num_hashes, false_positive_rates)
    plt.xlabel("Number of Hash Functions (k)")
    plt.ylabel("False Positive Rate")
    plt.title("False Positive Rate vs Number of Hash Functions in Bloom Filter")
    plt.show()


def plot_s_curve(num_bands, num_rows, thresholds, false_positive_rates):
    for i, b in enumerate(num_bands):
        plt.plot(thresholds, false_positive_rates[i], label=f"b={b}, r={num_rows[i]}")
    plt.xlabel("Threshold")
    plt.ylabel("Similarity Probability")
    plt.legend()
    plt.title("S-Curve Analysis for LSH")
    plt.show()
