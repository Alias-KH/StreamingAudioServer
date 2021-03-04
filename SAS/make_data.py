import pathlib
import sqlite3
import uuid
import ffmpeg
from ffprobe import FFProbe

#fetchをリスト型から辞書型に変換
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

HLS_PATH = pathlib.Path('./SAS/audio_hls')
SOURCE_PATH = pathlib.Path('./SAS/audio_source')
IMAGE_PATH = pathlib.Path('./SAS/image_hls')

EXTENSION_TUPLE = ('.flac', '.m4a')
DATABASE = 'AUDIO_SERVER.db'

con = sqlite3.connect(DATABASE)
con.row_factory = dict_factory

#SOURCE_PATHのサブディレクトリにある拡張子がEXTENSION_LISTの条件に当てはまるファイルパスの取得
audio_list = [f for f in list(SOURCE_PATH.glob('**/*')) if f.suffix in EXTENSION_TUPLE]

dir_path_list = []
for audio_file in audio_list:
    #大文字のキーと小文字のキーが混ざってるため全てのキーを小文字に変換
    metadata = {k.lower(): v for k, v in FFProbe(str(audio_file)).metadata.items()}
     
    #album_artist,album,title,track'のメタデータがない場合エラーを出す 未実装
    album_artist = metadata.get('album_artist')
    album = metadata.get('album')
    track = metadata.get('track')
    title = metadata.get('title')
    disc = metadata.get('disc')
    artist = metadata.get('artist')
    genre = metadata.get('genre')
    composer = metadata.get('composer')
    
    #テーブルに情報があるか確認
    #ない場合→データベースに情報を格納
    #ある場合→先の作業で必要になる場合があるidを保持

    sql3 = con.execute("SELECT * FROM track AS a INNER JOIN album AS b ON \
        a.album_id = b.album_id AND album =? AND track =?", (album, track,)).fetchone()
    if sql3 == None:
        sql2 = con.execute("SELECT * FROM album AS a INNER JOIN album_artist AS b ON \
            a.album_artist_id = b.album_artist_id AND album_artist =? AND album =?", (album_artist, album,)).fetchone()
        if sql2 == None:
            sql1 = con.execute("SELECT * FROM album_artist WHERE album_artist =?", (album_artist,)).fetchone()
            if sql1 == None:
                album_artist_id = str(uuid.uuid4())
                con.execute("INSERT INTO album_artist VALUES(?, ?)", (album_artist_id, album_artist,))
            else:
                album_artist_id = sql1.get('album_artist_id')
            
            album_id = str(uuid.uuid4())
            con.execute("INSERT INTO album VALUES(?, ?, ?)", (album_id, album_artist_id, album,))
        else:
            album_id = sql2.get('album_id')
            
        track_id = str(uuid.uuid4())
        con.execute("INSERT INTO track VALUES(?, ?, ?, ?, ?)", (track_id, album_id, title, track, disc,))
        con.execute("INSERT INTO metadata VALUES(?, ?, ?, ?)", (track_id, artist, genre, composer,))
        dir_path_list.append({'album_artist_id': album_artist_id, 'album_id': album_id, 'track_id': track_id, 'audio_path': str(audio_file), 'track': track})


#データベースに変更があった場合ディレクトリにも反映させる
try:
    for dir_path in dir_path_list:
        hls_dir = pathlib.Path(HLS_PATH / dir_path.get('album_artist_id') / dir_path.get('album_id') / dir_path.get('track_id'))
        hls_dir.mkdir(parents=True, exist_ok=True)
        
        input_stream = ffmpeg.input(dir_path.get('audio_path'))
        if dir_path.get('track') == '1':
            output_stream = ffmpeg.output(input_stream, str(IMAGE_PATH.resolve() / dir_path.get('album_id')) + '.jpg')
            ffmpeg.run(output_stream)
            
        output_stream = ffmpeg.output(input_stream, str(hls_dir.resolve() / 'output.m3u8'), \
            map='0:0', acodec='copy', strict='experimental', hls_playlist_type='vod', hls_segment_type='fmp4')
        ffmpeg.run(output_stream)
except NameError:
    pass

con.commit()
con.close()

# album_artist_list → {album_artist_ID: album_list}, {album_artist_ID: album_list}, ...
# album_list        → {album_ID: track_list}, {album_ID: track_list}, ...
# track_list        → {track_ID: {track: str(audio_file)}}, {track_ID: {track: str(audio_file)}}, ...

# album_artist_list[
#                   {album_artist_ID:[
#                                     {album_ID:[
#                                                {track_ID: {track: str(audio_file)}}
#                                                ]
#                                     }
#                                    ]
#                   }
#                  ]