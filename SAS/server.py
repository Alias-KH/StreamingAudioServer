from flask import Flask, jsonify, request
import sqlite3

DB_NAME = 'AUDIO_SERVER.db'

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route('/api/album_artist')
def album_artist_api():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM album_artist")
    rs = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    record_list = []
    for f in rs:
        record = {}
        record["album_artist_id"] = f[0]
        record["album_artist"] = f[1]
        record_list.append(record)
    
    return jsonify({"album_artist_list": record_list})

@app.route('/api/album/')
def album_api():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT album_id, album FROM album WHERE album_artist_id =?", (request.args.get('album_artist_id'),))
    rs = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    record_list = []
    for f in rs:
        record = {}
        record["album_id"] = f[0]
        record["album"] = f[1]
        record_list.append(record)
    
    return jsonify({"album_list": record_list})

@app.route('/api/track/')
def track_api():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT track_id, title, track, disc FROM track WHERE album_id =?", (request.args.get('album_id'),))
    rs = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    record_list = []
    for f in rs:
        record = {}
        record["track_id"] = f[0]
        record["title"] = f[1]
        record["track"] = f[2]
        record["disc"] = f[3]
        record_list.append(record)
    
    return jsonify({"track_list": record_list})

@app.route('/api/metadata/')
def metadata_api():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT artist, genre, composer FROM metadata WHERE track_id =?", (request.args.get('track_id'),))
    rs = cur.fetchall()
    
    conn.commit()
    conn.close()
    
    record_list = []
    for f in rs:
        record = {}
        record["artist"] = f[0]
        record["genre"] = f[1]
        record["composer"] = f[2]
        record_list.append(record)
    
    return jsonify({"metadata_list": record_list})

if __name__ == "__main__":
    app.run(port=50000)