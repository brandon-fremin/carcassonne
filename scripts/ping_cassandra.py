from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider  # Import for auth

import datetime

# Set up the auth provider with your username and password
auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')

# Connect to the cluster with authentication
cluster = Cluster(['127.0.0.1'], port=9042, auth_provider=auth_provider)

session = cluster.connect()

row = session.execute('SELECT release_version FROM system.local').one()
if row:
    print(f"Cassandra is reachable, release version: {row.release_version}")
else:
    print("No rows returned, but connected!")

session.execute("""
    CREATE KEYSPACE IF NOT EXISTS test_keyspace
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")
session.set_keyspace('test_keyspace')

session.execute("""
    CREATE TABLE IF NOT EXISTS kvstore (
        key         text PRIMARY KEY,
        value       text,
        timestamp   timestamp,
        version     int,
        metadata    map<text, text>
    );
""")

key = 'user123'
value = 'some data'
timestamp = datetime.datetime.now()
version = 1
metadata = {'source': 'app', 'env': 'prod'}

result = session.execute(
    """
    INSERT INTO kvstore (key, value, timestamp, version, metadata)
    VALUES (%s, %s, %s, %s, %s)
    IF NOT EXISTS;
    """,
    (key, value, timestamp, version, metadata)
)
if result[0].applied:
    print("Insert successful: row was created")
else:
    print("Insert failed: row already exists")


