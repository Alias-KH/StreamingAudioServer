import pathlib
import re
import sqlite3
import uuid
import ffmpeg
from ffprobe import FFProbe

HLS_PATH = pathlib.Path('./SAS/hls')
SOURCE_PATH = pathlib.Path('./SAS/audio_source')
EXTENSION = '.(flac|m4a)$'
DB_NAME = 'AUDIO_SERVER.db'

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

#SOURCE_PATHのサブディレクトリにある拡張子がEXTENSIONの条件に当てはまるファイル名を取得
audio_list = [f for f in list(SOURCE_PATH.glob('**/*')) if re.search(EXTENSION, str(f))]

for audio_file in audio_list:
    #大文字のキーと小文字のキーが混ざってるため全てのキーを小文字に変換
    audio_metadata = {k.lower(): v for k, v in FFProbe(str(audio_file)).metadata.items()}
    
    #データベースに情報を格納する準備
    album_artist = audio_metadata['album_artist']
    album = audio_metadata['album']
    title = audio_metadata['title']
    track = audio_metadata['track']
    disc = audio_metadata['disc']
    artist = audio_metadata['artist']
    genre = audio_metadata['genre']
    composer = audio_metadata['composer']
    
    #album_artistテーブルにすでに情報があるか確認
    cur.execute("SELECT * FROM album_artist WHERE album_artist =?", (album_artist,))
    sql1 = cur.fetchall()
    
    #ない場合→データベースに情報を格納　ある場合→先の作業で必要になる場合があるidを保持
    album_artist_id = ''
    if len(sql1) == 0:
        album_artist_id = str(uuid.uuid4())
        pathlib.Path(HLS_PATH / album_artist_id).mkdir()
        cur.execute("INSERT INTO album_artist VALUES(?, ?)", (album_artist_id, album_artist,))
    else:
        album_artist_id = sql1[0][0]
    
    #albumテーブルにすでに情報があるか確認
    cur.execute("SELECT * FROM album INNER JOIN \
        album_artist ON album.album_artist_id = album_artist.album_artist_id \
            WHERE album_artist =? AND album =?", (album_artist, album,))
    sql2 = cur.fetchall()
    
    #ない場合→データベースに情報を格納　ある場合→先の作業で必要になる場合があるidを保持
    artist_id = ''
    if len(sql2) == 0:
        album_id = str(uuid.uuid4())
        pathlib.Path(HLS_PATH / album_artist_id / album_id).mkdir()
        cur.execute("INSERT INTO album VALUES(?, ?, ?)", (album_id, album_artist_id, album,))
    else:
        album_id = sql2[0][0]
    
    #trackテーブルにすでに情報があるか確認
    cur.execute("SELECT * FROM track INNER JOIN \
        album ON track.album_id = album.album_id \
            WHERE album =? AND track =?", (album, track,))
    sql3 = cur.fetchall()
    
    #ない場合→データベースに情報を格納
    track_id = ''
    if len(sql3) == 0:
        track_id = str(uuid.uuid4())
        track_dir = pathlib.Path(HLS_PATH / album_artist_id / album_id / track_id)
        track_dir.mkdir()
        cur.execute("INSERT INTO track VALUES(?, ?, ?, ?, ?)", (track_id, album_id, title, track, disc,))
        cur.execute("INSERT INTO metadata VALUES(?, ?, ?, ?)", (track_id, artist, genre, composer,))
        
        stream = ffmpeg.input(str(audio_file))
        out_stream = ffmpeg.output(stream, str(track_dir.resolve()) + '/output.m3u8', \
            map='0:0', acodec='copy', strict='experimental', hls_playlist_type='vod', hls_segment_type='fmp4')
        try:
            ffmpeg.run(out_stream)
        except ffmpeg._run.Error as e:
            print(e)
    
    
    print(sql1)
    print(sql2)
    print(sql3)
    print('\n')
    
conn.commit()
conn.close()