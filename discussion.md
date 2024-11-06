# Discussion

## 1. Exploratory Data Analysis (EDA)

We began with exploratory data analysis (EDA) to get a sense of the dataset’s structure. This initial analysis allowed us to make informed choices about processing, filtering, and deduplication methods. Specifically, we looked at:
- **Document Lengths**: Document lengths varied widely, which helped us decide on flexible shingle sizes for Locality Sensitive Hashing (LSH).
- **Shingle Distribution**: Examining common shingles (n-grams) provided insight into which hash functions would best capture similarities among documents.
- **Baseline Duplicate Detection**: We implemented a baseline MD5 hash method to detect exact duplicates. This gave us a performance benchmark for more sophisticated methods like Bloom filters and LSH.

Overall, EDA confirmed that a single approach wouldn’t suffice to capture near-duplicates effectively. These insights laid the foundation for the rest of our work.

## 2. Engineering Decisions

### a. Preprocessing Steps
We applied several preprocessing steps to ensure consistency and improve deduplication accuracy:
- **Tokenization**: Splitting documents into trigrams (shingles of size 3) provided a good balance between capturing document features and avoiding excessive processing.
- **Normalization**: By converting text to lowercase and removing punctuation, we reduced variability in the data. This standardization reduced the likelihood of mismatches due to minor formatting differences.

### b. Bloom Filter Implementation
For the Bloom filter, we chose the `bitarray` library, which allowed efficient bit manipulation and memory savings. Initially, we observed a high false positive rate of around 0.45. To address this, we experimented with different values for the number of hash functions \( k \). 

Our first improvement involved reducing \( k \), which significantly lowered the false positive rate. Below is the plot showing the effect of varying \( k \):

![False Positive Rate vs. Number of Hash Functions](./falsepos.png)

The plot shows that fewer hash functions resulted in a lower false positive rate up to a point, after which the accuracy gains began to taper off.

### c. Optimized Bloom Filter with Counting
Building on the initial Bloom filter, we implemented a **counting Bloom filter**. This enhancement allowed us to dynamically add and remove items by incrementing or decrementing counts rather than setting a bit to 1. Implementing this functionality was particularly interesting because it allowed us to reduce false positives further, as well as manage memory efficiently.

The idea for the counting Bloom filter came from articles on the practical applications of Bloom filters, such as those on Analytics Vidhya. Using a counting Bloom filter enabled us to remove elements without affecting overall accuracy, which could be advantageous for real-time applications requiring dynamic adjustments.

## 3. LSH Implementations and Improvements

### a. Basic LSH
Our basic LSH implementation leveraged minhashing and banding to group similar documents into buckets. Minhashing generated a compact signature for each document, while banding helped us identify candidate pairs by comparing only certain portions of the signature. Although this approach was straightforward, we observed that minor variations in shingles occasionally caused similar documents to hash into different buckets.

The `lsh.py` file contains our primary implementation, including helper functions for minhashing, banding, and candidate generation. We focused on modularity here, allowing for easy testing and iterative improvements.

### b. Improved LSH
To improve the basic LSH implementation, we introduced two major changes:

1. **Adaptive Shingle Size Selection**: In the `LSHImproved` class, we implemented dynamic shingle sizing based on document length. Longer documents used larger shingles to reduce the total count without sacrificing essential information, while shorter documents used smaller shingles to maintain precision. This adjustment helped reduce processing time and memory usage.

2. **Multi-Probe LSH**: We introduced multi-probe functionality in the LSH, inspired by *Introduction to Information Retrieval*. Multi-probe LSH allows us to probe neighboring buckets in addition to the primary hash bucket, improving recall for near-duplicates that might otherwise fall into different buckets. This added complexity to the code, but the boost in accuracy was well worth the effort. 

### c. Union-Find Integration
In addition to multi-probe LSH, we implemented Union-Find to handle the clustering of similar documents. Our Union-Find implementation used path compression and union by rank to optimize cluster formation, which reduced redundancy and ensured efficient memory use.

## 4. Visualizations, Results, and Overall Analysis

### a. Bloom Filter Analysis
Here is a plot showing the impact of varying the number of hash functions \( k \) on the false positive rate:

![False Positive Rate vs. Number of Hash Functions](./falsepos.png)

This analysis helped us fine-tune the Bloom filter, ultimately deciding on an optimal \( k \) value that minimized false positives without excessive memory usage.

### b. LSH S-Curve Analysis
To determine the best banding configuration, we conducted an S-curve analysis by varying the number of bands \( b \) and rows \( r \). This analysis revealed the trade-offs between recall and precision, allowing us to choose parameters that maximized true positives while controlling false positives.

### c. Baseline Runtime and Results Summary

#### Baseline Approach
We began with an MD5-based baseline approach for exact duplicate detection, which provided valuable insights into processing speed and efficiency. Here’s a summary of the results:

| Dataset           | Number of Documents | Total Time (seconds) | Duplicate Pairs Found | Documents Processed per Minute |
|-------------------|---------------------|-----------------------|------------------------|--------------------------------|
| `threehundred.tsv` | 289                 | ~1                    | 16                     | 17,340                          |
| `onek.tsv`         | 996                 | ~1                    | 87                     | 59,760                          |
| `tenk.tsv`         | 9,995               | ~1                    | 1059                   | 599,700                         |

### Observations
- **Efficiency**: The MD5-based approach was highly efficient for exact duplicates, processing each dataset quickly and achieving high throughput.
- **Limitations**: While effective for exact duplicates, this method wasn’t suitable for near-duplicate detection, leading us to explore more complex techniques like LSH.

### d. LSH Implementation Runtime and Results Summary
We evaluated the LSH implementation using Union-Find clustering across datasets of varying sizes:

| Dataset           | Number of Documents | Start Time           | End Time             | Total Time (minutes) | Documents Processed Per Minute |
|-------------------|---------------------|----------------------|----------------------|-----------------------|---------------------------------|
| `threehundred.tsv` | 289                 | 17:36:06             | 17:37:12             | 1.10                  | ~262                             |
| `onek.tsv`         | 996                 | 17:37:12             | 17:40:59             | 3.78                  | ~263                             |
| `tenk.tsv`         | 9,995               | 17:41:00             | 18:16:10             | 35.17                 | ~284                             |

### Observations
- **Consistency**: The LSH method maintained a stable processing rate across datasets, suggesting scalability.
- **Memory Usage**: Using Python’s `memory_profiler`, we observed increased memory requirements for larger datasets, but Union-Find optimizations helped manage memory effectively.
- **Error Analysis**: A manual review of clustered documents showed that while most clusters were accurate, some included documents with only slight overlap, suggesting potential for further refinement in hash selection and shingle adjustments.

## 5. Challenges and Conclusions

### a. Challenges
- **Shingle Size Selection**: Choosing the right shingle size was challenging, as it affected recall and precision. We had to strike a balance to capture relevant similarities without adding noise.
- **Memory Management**: Scaling LSH required efficient memory handling to avoid slowdowns, especially with larger datasets. This experience taught us the importance of profiling and optimizing memory usage.
- **Complexity of Multi-Probe LSH**: Implementing and tuning multi-probe LSH was complex but ultimately worth it for the improved detection of near-duplicates.

### b. Conclusions
This project provided hands-on experience with scalable deduplication techniques. Combining Bloom filters with LSH, particularly with adaptive shingle sizing and multi-probe LSH, allowed us to balance precision, recall, and processing efficiency effectively.

Future work could involve further tuning of LSH parameters, exploring alternative hash functions, and implementing additional memory optimizations to enhance performance on even larger datasets. This project highlighted the power and scalability of combining Bloom filters and LSH for deduplication tasks and gave us valuable insights into the complexities of algorithmic optimization and resource management.
