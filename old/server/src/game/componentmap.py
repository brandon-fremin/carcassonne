from src.modules.jsondata import jsondata, List, Dict, Optional
from src.modules.decorators import protected
from src.game.component import Component
from src.game.tile import Tile
from src.game.feature import Feature, Conn
from src.game.types import FeatureType
import json
from src.modules.timer import timer_cb
import src.modules.logger as logger


@jsondata
class Component:
    id: str  # ID
    value: int  # current point value
    isCompleted: bool  # component is complete
    type: FeatureType  # road, city, ...
    features: Dict[str, List[str]]  # tileId -> featureIds
    includedTileIds: List[str]  # tile ids counting towards value


@jsondata
class ComponentMap:
    @jsondata
    class Node:
        tileId: str
        featureId: str
        featureType: FeatureType
        featureConns: List[Conn]
        i: int
        j: int
        right: bool
        top: bool
        left: bool
        bottom: bool

        def __init__(self, feature: Feature, tile: Tile):
            assert type(feature) is Feature
            assert type(tile) is Tile
            assert feature.id is not None
            assert feature.tileId == tile.id

            self.tileId = feature.tileId
            self.featureId = feature.id
            self.featureType = feature.type
            self.featureConns = feature.connections
            i, j = tile.transform.i, tile.transform.j
            self.i = i
            self.j = j
            self.right = not any([c.is_right() for c in feature.connections])
            self.top = not any([c.is_top() for c in feature.connections])
            self.left = not any([c.is_left() for c in feature.connections])
            self.bottom = not any([c.is_bottom() for c in feature.connections])

        def key(self) -> str:
            return ComponentMap.Node.to_key(self.tileId, self.featureId)

        def is_covered(self):
            return self.right and self.top and self.left and self.bottom

        def is_connected_to(self, other) -> bool:
            return ComponentMap.Node.connected(self, other)

        @staticmethod
        def to_key(tile_id: str, feature_id: str) -> str:
            return json.dumps([tile_id, feature_id])

        @staticmethod
        def from_key(key: str) -> List[int]:
            return json.loads(key)

        @staticmethod
        def left_right_connected(left_node, right_node) -> bool:
            assert type(left_node) is ComponentMap.Node
            assert type(right_node) is ComponentMap.Node

            l_cons = left_node.featureConns
            r_cons = right_node.featureConns
            return (
                left_node.featureType == right_node.featureType and
                left_node.i == right_node.i - 1 and
                left_node.j == right_node.j and
                (
                    (Conn.LT in r_cons and Conn.RT in l_cons) or
                    (Conn.LM in r_cons and Conn.RM in l_cons) or
                    (Conn.LB in r_cons and Conn.RB in l_cons)
                )
            )

        @staticmethod
        def top_bottom_connected(top_node, bottom_node) -> bool:
            assert type(top_node) is ComponentMap.Node
            assert type(bottom_node) is ComponentMap.Node

            t_cons = top_node.featureConns
            b_cons = bottom_node.featureConns
            return (
                top_node.featureType == bottom_node.featureType and
                top_node.i == bottom_node.i and
                top_node.j == bottom_node.j + 1 and
                (
                    (Conn.BL in t_cons and Conn.TL in b_cons) or
                    (Conn.BM in t_cons and Conn.TM in b_cons) or
                    (Conn.BR in t_cons and Conn.TR in b_cons)
                )
            )

        @staticmethod
        def connected(a, b) -> bool:
            return (
                ComponentMap.Node.left_right_connected(a, b) or
                ComponentMap.Node.left_right_connected(b, a) or
                ComponentMap.Node.top_bottom_connected(a, b) or
                ComponentMap.Node.top_bottom_connected(b, a)
            )

    nextNodeIdx: int
    nodes: Dict[str, List[Node]]  # componentId -> List[Node]
    tileIds: Dict[str, str]  # str(i, j) -> tileId

    @timer_cb(logger.info)
    def push(self, tile: Tile):
        assert type(tile) is Tile
        if tile.id in self.tileIds.values():
            return  # no-op

        self._add_tile(tile)
        for feature in tile.features:
            node = ComponentMap.Node(feature, tile)
            self._push_node(node)

    @timer_cb(logger.info)
    def get_components(self) -> Dict[str, Component]:
        return {
            component_id: self._make_component(component_id)
            for component_id in self.nodes.keys()
        }

    @staticmethod
    def to_position_key(i: int, j: int) -> str:
        return json.dumps([i, j])

    @staticmethod
    def to_component_id(i: int) -> str:
        return f"component{str(i).zfill(3)}"

    # @protected
    def _update_node_sides(self, node: Node):
        assert type(node) is ComponentMap.Node
        i, j = node.i, node.j
        node.right = self._tile_id_at(i + 1, j) or node.right
        node.top = self._tile_id_at(i, j + 1) or node.top
        node.left = self._tile_id_at(i - 1, j) or node.left
        node.bottom = self._tile_id_at(i, j - 1) or node.bottom

    # @protected
    def _tile_id_at(self, i: int, j: int) -> Optional[str]:
        assert type(i) is type(j) is int
        key = ComponentMap.to_position_key(i, j)
        return self.tileIds.get(key)

    # @protected
    def _add_tile(self, tile: Tile):
        i, j = tile.transform.i, tile.transform.j
        self.tileIds[ComponentMap.to_position_key(i, j)] = tile.id

    # @protected
    def _get_next_id(self) -> str:
        next_id = ComponentMap.to_component_id(self.nextNodeIdx)
        self.nextNodeIdx += 1
        return next_id

    # @protected
    def _push_node(self, node: Node):
        assert type(node) is ComponentMap.Node

        connected_ids = [
            component_id
            for component_id, other_nodes in self.nodes.items()
            for other_node in other_nodes
            if node.is_connected_to(other_node)
        ]

        self._meld_components(connected_ids, node)

        for nodes in self.nodes.values():
            for node in nodes:
                self._update_node_sides(node)

    # @protected
    def _meld_components(self, connected_ids: List[str], node: Node):
        next_id = self._get_next_id()
        if len(connected_ids) == 0:
            self.nodes[next_id] = [node]
        else:
            nodes = [node]
            for component_id in set(connected_ids):
                nodes.extend(self.nodes[component_id])
                del self.nodes[component_id]
            self.nodes[next_id] = nodes

    # @protected
    def _make_component(self, component_id: str):
        assert type(component_id) is str
        assert component_id in self.nodes.keys()
        nodes = self.nodes[component_id]
        assert type(nodes) is list
        assert len(nodes) > 0
        for node in nodes:
            assert type(node) is ComponentMap.Node
            assert node.featureType == nodes[0].featureType

        component = Component()
        component.id = component_id
        component.features = {
            node.tileId: [node.featureId for node in nodes]
            for node in nodes
        }
        component.isCompleted = self._is_completed(component_id)
        component.type = self._get_component_type(component_id)
        component.value = self._get_component_value(component_id)
        component.includedTileIds = self._get_component_tile_ids(component_id)
        return component

    # @protected
    def _is_completed(self, component_id: str) -> bool:
        return (
            component_id in self.nodes.keys() and
            all([node.is_covered() for node in self.nodes[component_id]])
        )

    # @protected
    def _get_component_type(self, component_id: str) -> FeatureType:
        assert component_id in self.nodes.keys()
        assert len(self.nodes[component_id]) > 0

        return self.nodes[component_id][0].featureType

    # @protected
    def _get_component_tile_ids(self, component_id: str) -> List[str]:
        assert component_id in self.nodes.keys()
        
        component_type = self._get_component_type(component_id)
        if component_type == FeatureType.Monastary:
            assert len(self.nodes[component_id]) == 1
            center_node = self.nodes[component_id][0]
            tile_ids = [
                self._tile_id_at(center_node.i + i, center_node.j + j)
                for i in [-1, 0, 1]
                for j in [-1, 0, 1]
            ]
            return [tile_id for tile_id in tile_ids if tile_id is not None]
        else:
            tile_ids = [node.tileId for node in self.nodes[component_id]]
            return list(set(tile_ids))

    # @protected
    def _get_component_value(self, component_id: str) -> int:
        assert component_id in self.nodes.keys()
        
        component_type = self._get_component_type(component_id)
        n = len(self._get_component_tile_ids(component_id))
        if component_type == FeatureType.Monastary:
            return n if self._is_completed(component_id) else n - 1
        elif component_type == FeatureType.Road:
            return n
        elif component_type == FeatureType.City:
            return 2 * n if self._is_completed(component_id) else n
        elif component_type == FeatureType.Field:
            return 0
        else:
            return -1
