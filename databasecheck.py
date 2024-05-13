import mysql.connector
from tmdbv3api import TMDb, Movie
import pandas as pd

# MySQL 연결 설정(정보 변경해야함)
mydb = mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="database_name"
)

mycursor = mydb.cursor()

# TMDB API 설정
tmdb = TMDb()
tmdb.api_key = 'your_tmdb_api_key' #TMDB api key
movie = Movie()

# description_list.csv에서 vod 제목 읽어오기
df_description = pd.read_csv('description_list.csv')
vod_titles = df_description['description'].tolist()

vod_id_list = []

for title in vod_titles:
    # MySQL 데이터베이스에 vod 제목이 있는지 확인 (수정해야함)
    mycursor.execute("SELECT * FROM vod_table WHERE title = %s", (title,))
    result = mycursor.fetchall()

    # 데이터베이스에 vod 제목이 없으면 TMDB API에서 데이터 가져오기
    if not result:
        # TMDB API에서 데이터 가져오기
        movie_search = movie.search(title)
        if movie_search:
            # 첫 번째 검색 결과 사용
            movie_info = movie_search[0]
            # 필요한 정보 추출(수정작업 필요)
            movie_id = movie_info.id
            movie_title = movie_info.title
            movie_overview = movie_info.overview
            movie_release_date = movie_info.release_date

            # MySQL 데이터베이스에 삽입(수정 필요)
            sql = "INSERT INTO vod_table (id, title, overview, release_date) VALUES (%s, %s, %s, %s)"
            val = (movie_id, movie_title, movie_overview, movie_release_date)
            mycursor.execute(sql, val)
            mydb.commit()

            print(f"Added {movie_title} to the database.")
            
            # 삽입된 영화의 ID를 리스트에 추가
            vod_id_list.append(movie_id)
        else:
            print(f"No data found for {title} in TMDB.")
    else:
        # 데이터베이스에 이미 있는 경우 해당 영화의 ID를 가져와서 리스트에 추가
        for row in result:
            vod_id_list.append(row[0])  # 여기서 0은 vod_table의 첫 번째 열인 ID를 의미합니다.

# 연결 닫기
mycursor.close()
mydb.close()

# vod_id_list 저장
print(vod_id_list)
