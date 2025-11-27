import logging, json
from dataclasses import dataclass

from src.common.utils import synchronized

from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider  # Import for auth


logger = logging.getLogger(__name__)


KEYSPACE = "tomstrainroom"


@dataclass
class TrackRecord:
    id: str
    name: str
    trackdata: dict
    metadata: dict


@dataclass
class LayoutRecord:
    id: str
    name: str
    layoutdata: dict
    metadata: dict


class CassandraClient:
    def __init__(
        self,
        username: str,
        password: str,
        hostname: str = "localhost",
        port: int = 9042,
    ):
        self._username = username
        self._auth_provider = PlainTextAuthProvider(
            username=username, password=password
        )
        self._cluster = Cluster(
            [hostname], port=port, auth_provider=self._auth_provider
        )
        self._session: Session = None

    def __del__(self):
        if self._session:
            self._session.shutdown()

    @synchronized
    def _connection(self) -> Session:
        if not self._session:
            self._session = self._cluster.connect()
        self._session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
        """
        )
        self._session.set_keyspace(KEYSPACE)
        self._session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS tracks (
                id          TEXT PRIMARY KEY,
                name        TEXT,
                metadata    TEXT,
                trackdata   TEXT
            )
        """
        )
        self._session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS layouts (
                id          TEXT PRIMARY KEY,
                name        TEXT,
                metadata    TEXT,
                layoutdata   TEXT
            )
        """
        )
        return self._session

    @synchronized
    def is_available(self):
        try:
            row = (
                self._connection()
                .execute("SELECT release_version FROM system.local")
                .one()
            )
            if row:
                logger.info(
                    f"Cassandra is reachable, release version: {row.release_version}"
                )
            return bool(row)
        except Exception as e:
            logger.error(f"Error checking Cassandra availability: {e}")
        return False

    def create_track(
        self, track: TrackRecord
    ) -> bool:
        session = self._connection()
        result = session.execute(
            """
            INSERT INTO tracks (id, name, trackdata, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (track.id, track.name, json.dumps(track.trackdata), json.dumps(track.metadata)),
        )
        return result.one().applied if result else False

    def get_tracks(self) -> list[TrackRecord]:
        session = self._connection()
        result = session.execute(
            """
            SELECT id, name, trackdata, metadata  FROM tracks;
            """
        )
        tracks = []
        for row in result:
            tracks.append(
                TrackRecord(
                    row.id,
                    row.name,
                    json.loads(row.trackdata) if row.trackdata else {},
                    json.loads(row.metadata) if row.metadata else {},
                )
            )
        return tracks

    def delete_track(self, track_id: str) -> bool:
        session = self._connection()
        result = session.execute(
            """
            DELETE FROM tracks WHERE id = %s IF EXISTS;
            """,
            (track_id,),
        )
        return result.one().applied if result else False

    def create_layout(self, layout: LayoutRecord) -> bool:
        session = self._connection()
        result = session.execute(
            """
            INSERT INTO layouts (id, name, layoutdata, metadata)
            VALUES (%s, %s, %s, %s)
            IF NOT EXISTS;
            """,
            (layout.id, layout.name, json.dumps(layout.layoutdata), json.dumps(layout.metadata)),
        )
        return result.one().applied if result else False

    def delete_layout(self, layout_id: str) -> bool:
        session = self._connection()
        result = session.execute(
            """
            DELETE FROM layouts WHERE id = %s IF EXISTS;
            """,
            (layout_id,),
        )
        return result.one().applied if result else False

    def update_layout(self, layout: LayoutRecord) -> bool:
        session = self._connection()
        result = session.execute(
            """
            UPDATE layouts 
            SET name = %s, layoutdata = %s, metadata = %s
            WHERE id = %s IF EXISTS;
            """,
            (layout.name, json.dumps(layout.layoutdata), json.dumps(layout.metadata), layout.id),
        )
        return result.one().applied if result else False

    def get_layout(self, layout_id: str) -> LayoutRecord | None:
        session = self._connection()
        result = session.execute(
            """
            SELECT id, name, layoutdata, metadata FROM layouts WHERE id = %s;
            """,
            (layout_id,),
        )
        row = result.one()
        if not row:
            return None
        return LayoutRecord(
            row.id,
            row.name,
            json.loads(row.layoutdata) if row.layoutdata else {},
            json.loads(row.metadata) if row.metadata else {},
        )

    def get_layouts(self) -> list[LayoutRecord]:
        session = self._connection()
        result = session.execute(
            """
            SELECT id, name, layoutdata, metadata FROM layouts;
            """
        )
        layouts = []
        for row in result:
            layouts.append(
                LayoutRecord(
                    row.id,
                    row.name,
                    json.loads(row.layoutdata) if row.layoutdata else {},
                    json.loads(row.metadata) if row.metadata else {},
                )
            )
        return layouts