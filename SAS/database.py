import sqlite3

DB_NAME = 'AUDIO_SERVER.db'

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("CREATE TABLE album_artist(album_artist_id TEXT, album_artist TEXT NOT NULL, \
    PRIMARY KEY(album_artist_id))")

cur.execute("CREATE TABLE album(album_id TEXT, album_artist_id TEXT, album TEXT NOT NULL, \
    PRIMARY KEY(album_id), FOREIGN KEY(album_artist_id) REFERENCES album_artist(album_artist_id))")

cur.execute("CREATE TABLE track(track_id TEXT, album_id TEXT, title TEXT NOT NULL, track INT NOT NULL, disc INT, \
    PRIMARY KEY(track_id), FOREIGN KEY(album_id) REFERENCES album(album_id))")

cur.execute("CREATE TABLE metadata(track_id TEXT, artist TEXT, genre TEXT, composer TEXT, \
    PRIMARY KEY(track_id), FOREIGN KEY(track_id) REFERENCES track(track_id))")

conn.commit()
conn.close()