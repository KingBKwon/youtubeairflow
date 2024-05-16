import mysql.connector
import pandas as pd
from pymongo import MongoClient


# MySQL 연결 설정(정보 변경해야함)
mydb = mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="database_name"
)
mycursor = mydb.cursor()


#MongoDB 연결 설정
connector = MongoClient("주소")
#DB 연결
db = connector.hellovision
#컬렉션 설정
collection = db.recommends

# description_list.csv에서 VOD 제목 읽어오기
df_description = pd.read_csv('description_list.csv')
vod_titles = df_description['description'].tolist()



# description_list.csv에서 vod 제목 읽어오기
df_description = pd.read_csv('description_list.csv')
vod_titles = df_description['description'].tolist()

vod_id_list = []

#MYSQL 가서 VOD_ID 가져오기
for title in vod_titles:
    # MySQL 데이터베이스에 vod 제목이 있는지 확인 (수정해야함)
    mycursor.execute("SELECT VOD_ID FROM movie_table WHERE title = %s", (title))
    result = mycursor.fetchall()
    # 영화에 vod 제목이 없으면 SERIES TABLE에서 데이터 가져오기
    if not result:
        mycursor.execute("SELECT VOD_ID FROM series_table WHERE title=%s",(title))
        result = mycursor.fetchall()
    # 결과가 있을 경우 VOD ID를 vod_id_list에 추가
    if result:
        vod_id_list.extend([vod_id[0] for vod_id in result])

# vod_id_list를 mongoDB 에 저장해야하는데 이미 있는 경우에는 수정해야함
#존재하는 모든 유저에 대한 수정작업이 필요
# 모든 사용자 문서 업데이트
for user_document in collection.find():
    existing_youtube_ids = user_document.get('Youtube', [])
    for vod_id in vod_id_list:
        if vod_id not in existing_youtube_ids:
            existing_youtube_ids.append(vod_id)
    collection.update_one(
        {'_id': user_document['_id']},
        {'$set': {'Youtube': existing_youtube_ids}}
    )

print("모든 사용자의 VOD ID가 업데이트되었습니다.")
# 연결 닫기
mycursor.close()
mydb.close()