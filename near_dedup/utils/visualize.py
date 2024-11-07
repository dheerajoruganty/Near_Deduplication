import numpy as np
import matplotlib.pyplot as plt
from near_dedup.lsh.lsh import LSH, LSHImproved # Import the class

# Define a range of similarities and multiple (b, r) configurations
similarities = np.linspace(0, 1, 100)  # Similarity values from 0 to 1
band_row_combinations = [(10, 2), (15, 3), (20, 4), (25, 5)]  # Different (b, r) configurations

# Plot S-curve for each (b, r) configuration
plt.figure(figsize=(10, 6))
for b, r in band_row_combinations:
    lsh_model = LSHImproved(num_bands=b, rows_per_band=r, num_hashes=100)
    probabilities = [lsh_model.calculate_probability(s) for s in similarities]
    plt.plot(similarities, probabilities, label=f"b={b}, r={r}")

# Customize the plot
plt.title("S-Curve for LSH with Multiple (b, r) Configurations")
plt.xlabel("Similarity")
plt.ylabel("Probability of Being in the Same Bucket")
plt.legend(title="(b, r) Configurations")
plt.grid()
plt.show()