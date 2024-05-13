#gmovie 실행
echo "Running gmovie file"
python3 ./gmovie/gmovie_crawling.py
python3 ./gmovie/gmovie_review_crawling.py
#실행완료
echo "gmovie scripts executed successfully"

#dreamteller 실행
echo "Running dreamteller file"
python3 ./dreamteller/dreamteller_crawling.py
python3 ./dreamteller/dreamteller_review_crawling.py
#실행완료
echo "dreamteller scripts executed successfully"

#gomong 실행
echo "Running gomong file"
python3 ./gomong/gomong_crawling.py
python3 ./gomong/gomong_review_crawling.py
#실행완료
echo "gomong scripts executed successfully"

#kimsiseon 실행
echo "Running kimsiseon file"
python3 ./kimsiseon/kimsiseon_crawling.py
python3 ./kimsiseon/kimsiseon_review_crawling.py
#실행완료
echo "kimsiseon scripts executed successfully"

#moviethink 실행
echo "Running moviethink file"
python3 ./moviethink/moviethink_crawling.py
python3 ./moviethink/moviethink_review_crawling.py
#실행완료
echo "moviethink scripts executed successfully"

#vod_review_predict.py 실행
python3 ./vod_review_predict.py

#databasecheck.py실행
python3 ./databasecheck.py

#실행완료
echo "success"

# Slack webhook URL과 메시지 설정
slack_webhook_url="https://hooks.slack.com/services/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"
message="YouTube recommendation script executed successfully"

# curl을 사용하여 Slack에 메시지 전송
curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$message"'"}' $slack_webhook_url