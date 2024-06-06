import pandas as pd
import requests
import mysql.connector
import csv
import json

# TMDB API 설정
TMDB_API_KEY = 'cd88d12bfe4c5d842ef9a464b2f0bcd1'

def search_tmdb(title):
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {title}: {e}")
        return None

def get_cast(tmdb_id, media_type):
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cast for ID {tmdb_id}: {e}")
        return None

# MySQL 연결 설정
db_config = {
    'user': 'root',
    'password': '12340131',
    'host': 'hellovision.c3gk86ic62pt.ap-northeast-2.rds.amazonaws.com',
    'database': 'hellovision'
}

try:
    # MySQL 연결
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # MOVIES 테이블에서 CAST 컬럼 조회
    cursor.execute("SELECT , VOD_ID, CAST FROM MOVIES")
    movies_data = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# CSV 파일 로드
description_list = pd.read_csv('description_list.csv', header=None)
description_list.columns = ['Title']

# 결과 저장을 위한 리스트
results = []

# 각 제목에 대해 처리
for index, row in description_list.iterrows():
    title = row['Title']
    search_result = search_tmdb(title)
    if search_result and 'results' in search_result and search_result['results']:
        first_result = search_result['results'][0]
        tmdb_id = first_result['id']
        media_type = first_result['media_type']
        cast_info = get_cast(tmdb_id, media_type)
        if cast_info and 'cast' in cast_info:
            for movie in movies_data:
                movie_title, vod_id, cast = movie
                if movie_title == title:
                    cast_list = json.loads(cast) if isinstance(cast, str) else cast
                    for actor in cast_info['cast']:
                        if actor['name'] in cast_list:
                            result_entry = [title, vod_id, actor['name']]
                            if result_entry not in results:
                                results.append(result_entry)

# 결과를 CSV 파일로 저장
with open('matched_results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "VOD_ID", "Actor"])
    writer.writerows(results)

# MySQL 연결 종료
cursor.close()
conn.close()
