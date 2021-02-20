import sqlite3
from flask import Flask, jsonify, request, make_response, g

DATABASE = 'AUDIO_SERVER.db'

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

#fetchをリスト型から辞書型に変換
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#データベースとコネクトする
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = dict_factory
    return db

#自動でデータベースをクローズする
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#APIで使う関数その1
def make_json_not_args(list_name, statement):
    return jsonify({list_name: get_db().execute(statement).fetchall()})

#APIで使う関数その2
def make_json_use_args(list_name, statement, args):
    return jsonify({list_name: get_db().execute(statement, (request.args.get(args),)).fetchall()})

#API
@app.route('/api/<api_request>/')
def api(api_request):
    if api_request == 'album_artist':
        return make_json_not_args('album_artist_list', "SELECT * FROM album_artist")
    
    elif api_request == 'album':
        return make_json_use_args('album_list', "SELECT album_id, album FROM album WHERE album_artist_id =?", 'album_artist_id')
    
    elif api_request == 'track':
        return make_json_use_args('track_list', "SELECT track_id, title, track, disc FROM track WHERE album_id =?", 'album_id')
    
    elif api_request == 'metadata':
        return make_json_use_args('metadata', "SELECT artist, genre, composer FROM metadata WHERE track_id =?", 'track_id')
    
    else:
        return('', 204)

#HLSをレスポンスする
@app.route('/<album_artist_id>/<album_id>/<track_id>/<file_name>')
def response_hls(album_artist_id, album_id, track_id, file_name):
    response = make_response()
    response.data  = open('./SAS/audio_hls/' + album_artist_id + '/' + album_id + '/' + track_id + '/' + file_name, "rb").read()
    
    if file_name == 'output.m3u8':
        response.headers['Content-Type'] = 'application/x-mpegurl'
    elif file_name == 'init.mp4':
        response.headers['Content-Type'] = 'video/mp4'
    else:
        response.headers['Content-Type'] = 'application/octet-stream'
    
    return response

if __name__ == "__main__":
    app.run(port=8080, threaded=True)