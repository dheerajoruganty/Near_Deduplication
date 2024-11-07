# Near Deduplication with Bloom Filters and LSH

![Pytest](https://img.shields.io/badge/Pytest-passing-brightgreen)




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
- [Documentation](#documentation)
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

1. **Install Git LFS**:

    ```bash
    git lfs install
    ```

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/DSAN6700-24Fall/assignment-2-five-guys.git
    cd assignment-2-five-guys
    ```

1. **Set Up the Conda Environment**:
    Ensure that you have Conda installed, and create an environment with Python 3.10.
    ```bash
    conda create --name five-guys -y python=3.10 ipykernel
    conda activate five-guys
    ```

1. **Install Dependencies**:
    Install the required dependencies.
    ```bash
    pip install -e .
    ```

## Usage


### 1. Bloom Filter:


You can run the bloom filter from `Examples` Folder in the Repository. There are 2 Jupyter notebooks, `Bloom_filter_exercises.ipynb` and `bloomfilterapplication.ipynb`


### 2. LSH Baselines, LSH and Improved LSH


Based on the `main.py` code provided, here are the updated instructions for running different deduplication methods, with commands tailored to the options available.

---

### Baseline Methods

You can run baseline deduplication methods to detect duplicates or near-duplicates based on different similarity metrics:

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

### Advanced Deduplication Methods (LSH and Bloom Filter)

Use the following commands to run advanced deduplication methods, including LSH and its variations.

1. **Standard LSH with *Union-Find* Deduplication**:
   This method detects near-duplicates using locality-sensitive hashing (LSH). You can specify the number of bands and rows per band for LSH configuration.

    ```bash
    python main.py --mode lsh --input_file data/thirty.tsv --num_bands 20 --rows_per_band 5 --num_hashes 100 --shingle_size 5
    ```

2. **Improved LSH Deduplication**:
   This optimized LSH method offers enhanced recall by using multiple probes. Set the number of additional probes using `--probes`.

    ```bash
    python main.py --mode improved_lsh --input_file data/thirty.tsv --num_bands 20 --rows_per_band 5 --num_hashes 100 --shingle_size 5 --probes 3
    ```

### Collection-Wide Deduplication with Bloom Filter and LSH

To perform deduplication on an entire collection using a combination of Bloom Filter and LSH, use the following:

```bash
python main.py --mode dedup --input_file data/thirty.tsv --num_bands 10 --rows_per_band 5 --num_hashes 100
```

---

### Notes on Output

All deduplication results will be saved to the `results/` directory, with each line representing a cluster of duplicate or near-duplicate documents identified by the algorithms.

The output filename is auto-generated based on the input file and deduplication algorithm, with a format like `results/30-lsh.txt` or `results/30-baseline-md5.txt`.

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

## Documentation:

This project includes a `gh-pages` branch for documentation, though it is not currently set up to be hosted on GitHub Pages. If you would like to view the documentation locally, follow the steps below.

## Building Documentation Locally

To build and view the documentation on your local machine:

1. **Navigate to the `docs` directory**:
   ```bash
   cd docs
   ```

2. **Install dependencies**:
   Make sure you have Sphinx and any necessary extensions installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the documentation**:
   Generate the HTML files by running:
   ```bash
   make html
   ```

4. **View the documentation**:
   Open the generated HTML files in a browser. The main entry point is:
   ```
   docs/build/html/index.html
   ```

## Note on the `gh-pages` Branch

The `gh-pages` branch is available in this repository for potential future hosting of documentation but is not actively being used to serve documentation online at this time.


## Contributors

This project was developed by:
- **Development Lead**: Dheeraj Oruganty, Pranav Patil, Will Corbin

For more information, see `AUTHORS.md`.

---

Thanks for checking out our project! If you have any questions or run into issues, please reach out to any of the contributors.
