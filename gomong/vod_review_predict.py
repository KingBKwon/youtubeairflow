import numpy as np
import pandas as pd
import re
import json
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import keras
import pickle
from tensorflow.keras.models import load_model
from datetime import datetime



# 데이터 전처리를 위한 불러오기
DATA_CONFIGS = 'data_configs.json'
prepro_configs = json.load(open(DATA_CONFIGS, 'r', encoding='utf-8'))
word_vocab = prepro_configs['vocab']


# 한국어 형태소 분석기 및 토크나이저 설정
okt = Okt()
tokenizer = Tokenizer()
tokenizer.fit_on_texts(word_vocab)

MAX_LENGTH = 8  # 문장 최대 길이
stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등', '한']  # 불용어 추가


    
model = keras.models.load_model('youtube_review/my_models/')
model.load_weights('youtube_review/cnn_classifier_kr_weights.h5')

# 모델 로드 및 문장 감성 분석 함수
def analyze_sentiment(sentence):
    sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣\\s ]', '', sentence)
    sentence = okt.morphs(sentence, stem=True)
    sentence = [word for word in sentence if not word in stopwords]
    vector = tokenizer.texts_to_sequences([sentence])
    pad_new = pad_sequences(vector, maxlen=MAX_LENGTH)
    prediction = model.predict(pad_new)
    return prediction.squeeze(-1)[0]

# 현재 주차 정보 가져오기
current_week = datetime.now().isocalendar()[1]

# 엑셀 파일에서 데이터 읽어오기
data = pd.read_excel(f'gomong_review_{current_week}주차.xlsx')

# 각 문장에 대해 감성 분석 수행하여 결과 추가
results = []
for comment in data['comment']:
    sentiment_score = analyze_sentiment(comment)
    sentiment = 1 if sentiment_score > 0.5 else 0
    results.append(sentiment)

# 결과를 새로운 열에 추가
data['sentiment'] = results

# video_id 별로 1이 차지하는 비율 계산
sentiment_ratio = data.groupby('video_id')['sentiment'].mean()

# sentiment_ratio가 0.5를 초과하는 video_id를 list로 저장
video_ids_over_05 = [video_id for video_id, ratio in sentiment_ratio.items() if ratio > 0.5]

#이제 gmovie_data 가져오기
df_videos = pd.read_csv(f'videos_data_gomong_{current_week}주차.csv')

description_list = []
for video_id in video_ids_over_05:
    description = df_videos.loc[df_videos['video_id'] == video_id, 'description'].values
    if len(description) > 0:
        # 리스트 안에 리스트가 있는 경우 풀어서 넣어주기
        descriptions = description[0].strip("[]").split(", ")
        for desc in descriptions:
            desc = desc.strip("'")
            if desc not in description_list:
                description_list.append(desc)
#결과물 출력
print(description_list)