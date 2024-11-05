

For the initial implementation of Bloom Filters, we chose the bitarray approach as opposed to the byte array approach.

To test the potential improvements to the bloom filter implementation, I created a list of unique words (length of 3653)to add into the bloom filter. After doing so, I took another list of unique words (length of 3653) to query in the bloom filter. This should mean that there are no false positives because they are all unique, yet the bloom filter will identify some as positive. I want to examine the false positive rate. I determined that this would be a good way to test the false positive rate from googling how to test false positive rates in bloom filters.

For the initial implementation of the bloom filter, before trying improvements, we had a very high false positive rate (0.45).

The first improvement I made was changing the number k of hash functions and just keeping a singular mmh3 hash function. Shrinking down the number of hash functions dramatically improved the false positive rate. The following graph shows how the less hash functions there were, the better the false positive rate.

![](./falsepos.png)

The next implementation I experimented with was a counting bloom filter. This ended up bringing the false positive rate down to about 0. I read about this implementation here: [https://medium.com/analytics-vidhya/cbfs-44c66b1b4a78]. I thought the counting bloom filter was interesting because you are now able to remove items. This was a unique implementation that I did not see befre. Basically instead of limiting a hash to 1, you are able to count upwards with each additional instance of an item. While adding the ability to remove items as well by subtracting values from the hash bit arrays. A byproduct of this implementation was the false positive rate dropping dramatically.


# Discussion on Improvements to LSH for Near-Duplicate Detection

## Worst-Case Scenario for LSH
The worst-case scenario for LSH in text deduplication occurs when similar documents fail to hash into the same bucket due to minor differences in shingles. ...

## Improvements and Rationale

LSHImproved class: adaptive shingle size selection. This improvement dynamically adjusts the shingle size for each document based on its length. The idea is that longer documents can have larger shingles, reducing the number of shingles generated while maintaining sufficient representation, whereas shorter documents use smaller shingles.

### 2. Multi-Probe LSH
Following [Introduction to Information Retrieval, Sec 3.4.2], we implemented multi-probe LSH. This allowed ...

...

## Results
We observed that ...
- Visualization 1: False positive rate vs. number of hash functions in the Bloom filter.
- Visualization 2: S-curve analysis of different band and row settings ...


# Discussion on LSH and Bloom Filter Improvements

## Worst-Case Scenario for LSH
In the worst-case scenario, similar documents might not hash into the same bucket due to slight variations in shingles ...

## Improvements Implemented

### Adjustable Shingle Size
Based on [Mining of Massive Datasets, Sec 3.2.2], we experimented with various shingle sizes to ...

### Multi-Probe LSH
Following [Introduction to Information Retrieval, Sec 3.4.2], we implemented multi-probe LSH. This increased ...

## Results
- For Bloom Filter: see Figure 1 for false positive rate vs. number of hash functions.
- For LSH: see Figure 2 for S-curve analysis ...

### Choices Made in Implementation
1. **Document Processing**: We normalized the text by ...
2. **Shingle Size**: Shingle size was set to ...


## Runtime and Processing Efficiency

To calculate the "Documents Processed per Minute" for each dataset, we use the following formula:

\[
\text{Documents Processed per Minute} = \frac{\text{Number of Documents}}{\text{Total Time (in minutes)}}
\]

Given that each of the MD5 baseline runs completed in approximately 1 second, we can compute the documents processed per minute as follows:

---

## Baseline Runtime and Results Summary

### Baseline Approach

The MD5-based baseline deduplication was applied to datasets of various sizes to detect exact duplicates. Below is the summary of the results, including the number of duplicate pairs detected, runtime efficiency, and the calculated documents processed per minute.

| Dataset           | Number of Documents | Total Time (seconds) | Duplicate Pairs Found | Documents Processed per Minute |
|-------------------|---------------------|-----------------------|------------------------|--------------------------------|
| `threehundred.tsv` | 289                 | ~1                    | 16                     | 17,340                          |
| `onek.tsv`         | 996                 | ~1                    | 87                     | 59,760                          |
| `tenk.tsv`         | 9,995               | ~1                    | 1059                   | 599,700                         |

### Observations

- **Duplicate Detection**: The MD5 hashing approach effectively detected exact duplicates in all datasets, with larger datasets containing more duplicate pairs.
  
- **Efficiency**: The MD5-based deduplication processed each dataset very quickly, achieving high throughput rates, as shown in the "Documents Processed per Minute" column. Even for the largest dataset (`tenk.tsv`), it handled nearly 600,000 documents per minute.

- **Scalability**: This baseline implementation is both efficient and highly scalable for exact duplicate detection. However, it cannot detect near-duplicates, which will be addressed by implementing LSH.


### LSH Implementation

To evaluate the efficiency of the LSH implementations, we tested the Union-Find LSH method across three datasets of varying sizes. The following table summarizes the runtime for each dataset, including the total time taken, documents processed per minute, and observations on scalability.

| Dataset           | Number of Documents | Start Time           | End Time             | Total Time (minutes) | Documents Processed Per Minute |
|-------------------|---------------------|----------------------|----------------------|-----------------------|---------------------------------|
| `threehundred.tsv` | 289                 | 17:36:06             | 17:37:12             | 1.10                  | ~262                             |
| `onek.tsv`         | 996                 | 17:37:12             | 17:40:59             | 3.78                  | ~263                             |
| `tenk.tsv`         | 9,995               | 17:41:00             | 18:16:10             | 35.17                 | ~284                             |

### Observations

- **Consistency Across Datasets**: The Union-Find LSH method maintained a fairly consistent processing rate of around 260–280 documents per minute, regardless of the dataset size. This consistency indicates that the method scales linearly with dataset size, which is promising for larger document collections.
  
- **Memory Usage**: Memory usage was monitored by using Python’s `memory_profiler` package, which allowed us to track peak memory consumption during processing. As expected, the larger datasets required more memory due to the higher volume of document shingle storage and hash computations. However, with Union-Find optimizations, we minimized redundant memory usage by clustering similar documents efficiently.
  
- **Error Analysis**: To evaluate the quality of deduplication, we traced a sample of document clusters back to their raw content. Results show that while most clusters accurately grouped near-duplicates, a few clusters included documents with marginal content overlap. This highlights a potential improvement area for more selective hash functions or adjustable shingle sizes.

This analysis demonstrates that while the Union-Find LSH implementation is effective and scalable, adjustments in hash selection, shingle size, and memory optimization can further enhance its performance and accuracy.

---

This section provides a structured summary of your observations, including runtime data, memory usage insights, and error analysis based on your experiment findings.