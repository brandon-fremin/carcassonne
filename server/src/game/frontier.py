from src.modules.jsondata import jsondata, List, Dict, Optional
from src.game.tile import Tile
from src.modules.decorators import protected
import json
from src.modules.timer import timer_cb
import src.modules.logger as logger


@jsondata
class Frontier:
    @jsondata
    class Node:
        tileId: Optional[str]
        i: int
        j: int
        right: bool
        top: bool
        left: bool
        bottom: bool

        def __init__(self, i: int, j: int):
            assert type(i) is int
            assert type(j) is int
            self.tileId = None
            self.i = i
            self.j = j
            self.right = self.top = self.left = self.bottom = False

        @staticmethod
        def to_key(i: int, j: int) -> str:
            return json.dumps([i, j])

        @staticmethod
        def from_key(key: str) -> List[int]:
            return json.loads(key)

        def key(self) -> str:
            return Frontier.Node.to_key(self.i, self.j)

        def is_covered(self) -> bool:
            return self.right and self.top and self.left and self.bottom

        def is_frontier(self) -> bool:
            return self.tileId is None

    nodes: Dict[str, Node]  # str(i, j) -> Node
    tileIds: Dict[str, str]  # str(i, j) -> tileId

    @timer_cb(logger.info)
    def push(self, tile: Tile):
        # verify
        assert type(tile) is Tile
        return self._push(tile.id, tile.transform.i, tile.transform.j)
    
    def tile_id_at(self, i: int, j: int) -> str:
        key = Frontier.Node.to_key(i, j)
        if key in self.tileIds.keys():
            return self.tileIds[key]
        return None

    def node_at(self, i: int, j: int) -> Node:
        key = Frontier.Node.to_key(i, j)
        if key in self.nodes.keys():
            return self.nodes[key]
        return None

    def size(self):
        return len(self.frontier_nodes())

    def frontier_nodes(self, is_frontier=True):
        if is_frontier:
            return [n for n in self.nodes.values() if n.is_frontier()]
        else:
            return [n for n in self.nodes.values() if not n.is_frontier()]

    # @protected
    def _push(self, tileId: Optional[str], i: int, j: int):
        assert type(tileId) in [str, type(None)]
        assert type(i) is type(j) is int

        if tileId in self.tileIds.values():
            return  # no-op
        
        key = Frontier.Node.to_key(i, j)
        if key not in self.nodes.keys():
            self.nodes[key] = Frontier.Node(i, j)
        node = self.nodes[key] 

        if tileId is not None:
            self.tileIds[key] = node.tileId = tileId
            self._ensure_node_at(i + 1, j)  # right
            self._ensure_node_at(i, j + 1)  # top
            self._ensure_node_at(i - 1, j)  # left
            self._ensure_node_at(i, j - 1)  # bottom

        self._update_node_at(i + 1, j)  # right
        self._update_node_at(i, j + 1)  # top
        self._update_node_at(i - 1, j)  # left
        self._update_node_at(i, j - 1)  # bottom
        self._update_node_at(i, j)  # self

    # @protected
    def _update_node_at(self, i: int, j: int):
        assert type(i) is int
        assert type(j) is int
        node = self.node_at(i, j)
        if node is None:
            return

        node.right = bool(self.tile_id_at(i + 1, j))
        node.top = bool(self.tile_id_at(i, j + 1))
        node.left = bool(self.tile_id_at(i - 1, j))
        node.bottom = bool(self.tile_id_at(i, j - 1))
    
    # @protected
    def _ensure_node_at(self, i: int, j: int):
        node = self.node_at(i, j)
        if node is None:
            self._push(None, i, j)
