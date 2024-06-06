import pandas as pd
import requests
import mysql.connector
import csv
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import csv


#TMDB API KEY 불러오기
load_dotenv()
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')

# MySQL 데이터베이스 설정
db_config = {
    'host': os.getenv('db_host'),
    'user': os.getenv('db_user'),
    'password': os.getenv('db_password'),
    'database': os.getenv('db_name')
}


try:
    # MySQL 연결
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(f"MySQL 연결 중 오류 발생: {err}")
    exit(1)

# Mongodb 접속권한
mongodb_url = os.environ.get('mongodb_url')
db_name = os.environ.get('mongodb_name')
db_collection = os.environ.get('collection')
client = MongoClient(mongodb_url)
db = client[db_name]
collection = db[db_collection]


#tmdb 제목 검색
def search_tmdb(title):
    """주어진 제목으로 TMDB 검색"""
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{title}에 대한 데이터를 가져오는 중 오류 발생: {e}")
        return None

#tmdb_id로 배우 저장
def get_cast(tmdb_id, media_type):
    """미디어 ID와 타입을 사용하여 TMDB에서 출연진 정보 가져오기"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits?api_key={TMDB_API_KEY}&language=ko-KR"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ID {tmdb_id}에 대한 출연진 정보를 가져오는 중 오류 발생: {e}")
        return None

# CSV 파일 로드
description_list = pd.read_csv('description_list.csv', header=None)
description_list.columns = ['Title']

# VOD_ID를 저장할 리스트
vod_id_list = []

# 각 제목에 대해 배우 정보 출력 및 해당 배우가 포함된 영화 제목 출력
for index, row in description_list.iterrows():
    title = row['Title']
    if pd.isna(title):
        continue  # 제목이 'nan'인 경우 건너뜁니다.
    search_result = search_tmdb(title)
    if search_result and 'results' in search_result and search_result['results']:
        first_result = search_result['results'][0]
        tmdb_id = first_result['id']
        media_type = first_result['media_type']
        cast_info = get_cast(tmdb_id, media_type)
        if cast_info and 'cast' in cast_info:
            print(f"제목: {title}")
            actor_list = [actor['name'] for actor in cast_info['cast']]
            for actor_name in actor_list:
                print(f"  배우: {actor_name}")
                # 배우 이름이 포함된 영화 검색
                query = "SELECT TITLE, VOD_ID, POSTER FROM MOVIES WHERE CAST LIKE %s"
                cursor.execute(query, (f"%{actor_name}%",))
                matched_movies = cursor.fetchall()
                for matched_movie in matched_movies:
                    movie_title, vod_id, poster_url = matched_movie
                    vod_id_list.append(vod_id)
                    #print(f"    포함된 영화 제목: {movie_title}, VOD_ID: {vod_id}, 포스터 URL: {poster_url}")
        else:
            print(f"{title}에 대한 출연진 정보가 없습니다.")
    else:
        print(f"{title}에 대한 검색 결과가 없습니다.")

# 모든 VOD_ID에 해당하는 영화 정보 조회 및 CSV 저장
result_data = []

for vod_id in vod_id_list:
    query = "SELECT TITLE, POSTER, VOD_ID FROM MOVIES WHERE VOD_ID = %s"
    cursor.execute(query, (vod_id,))
    movie_info = cursor.fetchone()
    if movie_info:
        title, poster_url, vod_id = movie_info
        result_data.append([vod_id, poster_url, title])
        #print(f"제목: {title}, 포스터 URL: {poster_url}, VOD_ID: {vod_id}")

# 중복 제거
df = pd.DataFrame(result_data, columns=['VOD_ID', 'POSTER', 'TITLE'])
df.drop_duplicates(subset=['VOD_ID'], inplace=True)
# CSV 파일로 저장
csv_filename = 'vod_movies.csv'
df.to_csv(csv_filename, index=False, encoding='utf-8')
print(f"모든 선택된 영화 정보가 중복을 제거하여 {csv_filename} 파일로 저장되었습니다.")

# CSV 파일 로드
df = pd.read_csv('vod_movies.csv')

# 각 행을 딕셔너리로 변환
youtube_list = df.to_dict('records')

# 모든 사용자의 youtube 리스트를 업데이트
collection.update_many({}, {'$set': {'youtube': youtube_list}})

print(f"모든 사용자의 youtube 리스트가 csv 파일의 내용으로 업데이트되었습니다.")


# MySQL 연결 종료
cursor.close()
conn.close()

