class UnionFind:
    """
    Union-Find data structure to support clustering of similar documents.
    """

    def __init__(self):
        """
        Initialize the Union-Find data structure.
        """
        self.parent = {}
        self.rank = {}

    def find(self, x: int) -> int:
        """
        Find the root of x with path compression.
        @param x: Element to find
        @return: Root of x
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int):
        """
        Union by rank to merge two sets containing x and y.
        @param x: First element
        @param y: Second element
        """
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

    def add(self, x: int):
        """
        Add a new element to the Union-Find structure.
        @param x: Element to add
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
