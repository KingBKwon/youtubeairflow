import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.environ.get('API_KEY')
# YouTube Data API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=API_KEY)

#video_id 가져오는 list
video_id = {}

# 현재 주차 정보 가져오기
current_week = datetime.now().isocalendar()[1]

# CSV 파일 경로 생성
csv_file_path = f'videos_data_gomong_{current_week}주차.csv'

# 동영상 ID를 저장할 리스트 초기화
video_ids = []

# CSV 파일에서 video_id 가져오기
try:
    df = pd.read_csv(csv_file_path)
    video_ids = df['video_id'].tolist()
except FileNotFoundError:
    print(f'Error: {csv_file_path} not found!')
    exit()

#print(video_ids)


#댓글 가져오는 list 
comments = []

 
# YouTube API를 사용하여 댓글 가져오기
for video_id in video_ids:
    try:
        api_obj = build('youtube', 'v3', developerKey=API_KEY)
        response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()
        
        while response:
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append([video_id, comment['textDisplay'], comment['likeCount']])
            
            if 'nextPageToken' in response:
                response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
            else:
                break
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')

# DataFrame 생성
df_comments = pd.DataFrame(comments, columns=['video_id', 'comment', 'num_likes'])

# 댓글 데이터를 저장할 Excel 파일 경로 생성
file_name = f'gomong_review_{current_week}주차.xlsx'

# DataFrame을 Excel 파일로 저장
df_comments.to_excel(file_name, header=True, index=None)

print(f'File saved as {file_name}')
