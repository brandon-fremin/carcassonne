from src.modules.jsondata import jsondata


@jsondata
class Node:
    i: int
    j: int
    isSearched: bool
    isFrontier: bool

    def __init__(self, i: int, j: int):
        assert type(i) is int
        assert type(j) is int
        self.i = i
        self.j = j
        self.isSearched = False
        self.isFrontier = True


def update_frontier(self):
    if len(self.frontier) == 0:
        self.frontier = [Node(i=0, j=0)]
    for node in self.frontier:
        node.isSearched = False

    def find(i: int, j: int) -> bool:
        for tile in self.tiles.values():
            if tile.transform.i == i and tile.transform.j == j:
                return True
        return False

    def expand(i: int, j: int) -> list[dict]:
        # Make sure we don't already have this node
        for node in self.frontier:
            if node.i == i and node.j == j:
                return
        # Add tile to frontier
        self.frontier.append(Node(i=i, j=j))

    n = 0
    while len(self.frontier) > n:
        n = len(self.frontier)

        for node in self.frontier:
            if node.isSearched:
                continue

            node.isSearched = True
            i, j = node.i, node.j
            tile = find(i, j)
            if tile:
                node.isFrontier = False
                expand(i - 1, j)
                expand(i + 1, j)
                expand(i, j - 1)
                expand(i, j + 1)
