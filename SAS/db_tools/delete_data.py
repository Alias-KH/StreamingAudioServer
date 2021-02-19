import sqlite3

DB_NAME = 'AUDIO_SERVER.db'

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("DROP TABLE album_artist")
cur.execute("DROP TABLE album")
cur.execute("DROP TABLE track")
cur.execute("DROP TABLE metadata")

conn.commit()
conn.close()