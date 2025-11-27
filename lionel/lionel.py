import sqlite3
import plistlib
import struct
from functools import wraps

conn = sqlite3.connect("Lionel_LCS.sqlite")
cur = conn.cursor()

cur.execute("SELECT Z_PK, ZTRACKDATAEXTRA FROM ZTRACKDATA LIMIT 1")
rows = cur.fetchall()

def nothrow(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(func.__qualname__, type(e), e)
    return wrapper

@nothrow
def as_plist_str(blob: bytes) -> dict | None:
    return plistlib.loads(blob.decode())

@nothrow
def as_plist(blob: bytes) -> dict | None:
    return plistlib.load(blob)

@nothrow
def test1(blob: bytes):
    # Example: unpack first 4 bytes as integer
    first_int = struct.unpack(">I", blob[0:4])[0]  # big-endian
    # Next 8 bytes as double (for X coordinate)
    x_coord = struct.unpack(">d", blob[4:12])[0]
    # Next 8 bytes as double (for Y coordinate)
    y_coord = struct.unpack(">d", blob[12:20])[0]
    print(f"Row {pk}: first_int={first_int}, X={x_coord}, Y={y_coord}")


@nothrow
def test2(blob: bytes):        
    track_id, track_type, x, y, orientation = struct.unpack(">IIddI", blob[:28])
    print(f"Row {pk}: id={track_id}, type={track_type}, x={x}, y={y}, orient={orientation}")

for pk, blob in rows:
    # print(blob, type(blob))
    print(f"Row {pk}")
    as_plist(blob)
    as_plist_str(blob)
    test1(blob)
    test2(blob)