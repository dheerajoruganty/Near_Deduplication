# Near Deduplication with Bloom Filters and LSH

<p align="center">
<a href="https://pypi.python.org/pypi/near_dedup">
    <img src="https://img.shields.io/pypi/v/near_dedup.svg"
        alt="Release Status">
</a>

<a href="https://dheerajoruganty.github.io/near_dedup/">
    <img src="https://img.shields.io/website/https/dheerajoruganty.github.io/near_dedup/index.html.svg?label=docs&down_message=unavailable&up_message=available" alt="Documentation Status">
</a>

<a href="https://pyup.io/repos/github/dheerajoruganty/near_dedup/">
<img src="https://pyup.io/repos/github/dheerajoruganty/near_dedup/shield.svg" alt="Updates">
</a>
</p>

This repository provides code for detecting exact and near-duplicate documents using Bloom Filters and Locality Sensitive Hashing (LSH). It also includes baseline methods for exact duplicates (MD5 hashing) and similarity-based deduplication (N-Gram and Jaccard similarity). The goal is to offer an efficient solution for large-scale deduplication by leveraging memory-efficient data structures and hash-based clustering.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Baseline Methods](#baseline-methods)
  - [LSH and Bloom Filters](#lsh-and-bloom-filters)
- [Environment Setup](#environment-setup)
- [Results](#results)
- [Contributors](#contributors)

---

## Project Overview

The deduplication solution provided here is capable of detecting:
- **Exact Duplicates**: Using MD5 hashing as a baseline method.
- **Near Duplicates**: Using LSH with customizable parameters and Bloom Filters optimized with N-Gram and Jaccard similarity options.

This solution is useful for deduplication tasks where document similarities must be efficiently identified and grouped, especially in cases where large-scale data is involved. Bloom Filters offer memory-efficient exact duplicate detection, while LSH allows for scalable near-duplicate detection by reducing the number of required comparisons.

## Features

- **Bloom Filter Implementation**: Efficient memory structure for detecting exact duplicates.
- **Counting Bloom Filter**: Dynamic Bloom Filter version that allows items to be added and removed, reducing false positives.
- **Locality Sensitive Hashing (LSH)**: Minhashing-based technique that clusters similar documents.
- **Multi-Probe LSH**: Enhanced LSH to improve recall by probing additional hash buckets.
- **Baseline Methods**: MD5, N-Gram, and Jaccard similarity baselines to benchmark the effectiveness of LSH and Bloom Filter implementations.
- **Automated Testing and CI**: Continuous integration setup with GitHub Actions for automated testing.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/DSAN6700-24Fall/assignment-2-five-guys.git
    cd assignment-2-five-guys
    ```

2. **Set Up the Conda Environment**:
    Ensure that you have Conda installed, and create an environment with Python 3.10.
    ```bash
    conda create --name five-guys -y python=3.10 ipykernel
    conda activate five-guys
    ```

3. **Install Dependencies**:
    Install the required dependencies.
    ```bash
    pip install -e .
    ```

## Usage

### Baseline Methods

You can run the baseline deduplication methods to detect duplicates or near-duplicates based on different similarity metrics:

1. **MD5 Baseline (Exact Duplicate Detection)**:
    ```bash
    python main.py --mode baseline --baseline md5 --input_file data/thirty.tsv
    ```

2. **N-Gram Baseline**:
    ```bash
    python main.py --mode baseline --baseline ngram --n 3 --threshold 0.8 --input_file data/thirty.tsv
    ```

3. **Jaccard Baseline**:
    ```bash
    python main.py --mode baseline --baseline jaccard --threshold 0.7 --input_file data/thirty.tsv
    ```

### LSH and Bloom Filters

To run the advanced LSH and Bloom Filter deduplication methods, use the following commands. These commands allow you to configure the deduplication process to detect exact duplicates (Bloom Filter) or near-duplicates (LSH).

1. **Run Bloom Filter for Exact Duplicates**:
    ```bash
    python main.py --mode bloom --input_file data/thirty.tsv
    ```

2. **Run LSH Deduplication**:
    ```bash
    python main.py --mode lsh --input_file data/thirty.tsv --bands 20 --rows 5
    ```

3. **Run Multi-Probe LSH for Enhanced Recall**:
    ```bash
    python main.py --mode multiprobe_lsh --input_file data/thirty.tsv --bands 20 --rows 5 --probes 3
    ```

These scripts will generate output in the `results/` directory, where each line represents a cluster of duplicate or near-duplicate documents detected by the algorithms.

### Customizing Parameters

- **Shingle Size**: Modify the `deduplicator.py` script to change the shingle size for adapting to different types of documents.
- **Hash Functions**: Adjust the number of hash functions in `bloom_filter.py` and `lsh.py` for customized accuracy and efficiency.

## Environment Setup

To ensure compatibility across different environments, install the required packages and dependencies on a fresh machine. Testing the setup this way ensures that there are no missing dependencies or environment issues.

1. **Environment Variables**: Set up any necessary environment variables as specified in the configuration files.
2. **Data Path**: Place your input datasets in the `data/` directory or specify custom paths in the command line.

## Results

All output files are saved in the `results/` directory. The naming convention follows `{dataset}-{algorithm}.txt` (e.g., `thirty-lsh.txt`), where each file contains clusters of identified duplicates. For example:

```bash
123 456 789 # Documents 123, 456, and 789 are near-duplicates 101 202 303 ...
```


This directory structure ensures that all results are easily accessible and organized for analysis.

## Contributors

This project was developed by:
- **Development Lead**: Dheeraj Oruganty, Pranav Patil, Will Corbin

For more information, see `AUTHORS.md`.

---

This README offers an overview of the deduplication project, usage instructions, and details on how to set up the environment and access results. If you have questions, please reach out to any of the contributors.
