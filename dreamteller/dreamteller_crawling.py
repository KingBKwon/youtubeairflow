from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#import pprint
import csv
import re
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get('API_KEY')

#dreamteller channel external id
dreamteller_channel_id = 'UCpCiIDf9UrfRqte55FHWlYQ'

#youTube Data API 클라이언트 생성
youtube = build('youtube','v3',developerKey=API_KEY)

beforeVideos = []

try:
  #동영상 목록 가져오기
  request = youtube.search().list(
    part='id,snippet',
    channelId = dreamteller_channel_id,
    order='date',
    type='video',
    videoDuration='medium',
    maxResults=10
  )
  response = request.execute()
  #pprint.pprint(response)
  
  #동영상 제목과 ID 추출
  for item in response['items']:
    video_title = item['snippet']['title']
    video_id = item['id']['videoId']
    description = item['snippet']['description']
    #print(f'{video_title}:{video_id}')
    #전처리 해서 #드라마 #영화랑 <<vod제목>>만 남게 해줘 
    #description = description

    # 정규 표현식을 사용하여 패턴에 맞는 문자열 찾기
    description= re.findall(r'\[(.*?)\]', description)
    beforeVideos.append({'video_title': video_title, 'video_id': video_id, 'description':description})
    

  # 현재 주차 정보 가져오기
  current_week = datetime.now().isocalendar()[1]

  # CSV 파일로 저장
  csv_file = f'videos_data_dreamteller_{current_week}주차.csv'
  with open(csv_file, 'w', newline='', encoding='utf-8') as file:
      writer = csv.DictWriter(file, fieldnames=['video_title', 'video_id', 'description'])
      writer.writeheader()
      for video in beforeVideos:
          writer.writerow({'video_title': video['video_title'], 'video_id': video['video_id'], 'description': video['description']})
  print(f'Videos data saved to {csv_file}')
  
except HttpError as e:
  print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
  

