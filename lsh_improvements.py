class LSHImproved(LSHWithUnionFind):
    """
    Extended LSH with improvements like Universal Hashing and Multi-probe LSH.
    """

    def universal_hashing(self, shingle: str) -> int:
        """
        Universal hashing function.
        @param shingle: Shingle to hash
        @return: Hashed value
        """
        return int(hashlib.sha256(shingle.encode()).hexdigest(), 16)

    def multi_probe_banding(self, signature: List[int], probes: int = 1) -> List[int]:
        """
        Multi-probe LSH to explore neighboring buckets.
        @param signature: Minhash signature
        @param probes: Number of additional probes
        @return: List of hash values for bands including probes
        """
        band_hashes = super().banding(signature)
        probe_hashes = []
        for band_hash in band_hashes:
            probe_hashes.append(band_hash)
            for probe in range(1, probes + 1):
                probe_hashes.append(band_hash + probe)
                probe_hashes.append(band_hash - probe)
        return probe_hashes