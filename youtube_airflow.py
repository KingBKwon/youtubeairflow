import json
import pathlib
import airflow.utils.dates
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum

kst = pendulum.timezone("Asia/Seoul")

# DAG 인스턴스 생성
with DAG(
    dag_id="youtube_dag",
    description="YouTube update",
    start_date=datetime(2024, 6, 6, tzinfo=kst),
    schedule_interval=timedelta(days=1)  # 하루에 한번씩 실행
) as dag:

    t1a = BashOperator(
        task_id='gmoviecrawling',
        bash_command='python3 home/ubuntu/airflow/dags/youtubeairflow/gmovie/gmovie_crawling.py',
    )
        
    t1b = BashOperator(
        task_id='gmoviereviewcrawling',
        bash_command='python3 python3 /home/ubuntu/airflow/dags/youtubeairflow/gmovie/gmovie_review_crawling.py',
    )

    t2a = BashOperator(
        task_id='dreamtellercrawling',
        bash_command='python3 python3 /home/ubuntu/airflow/dags/youtubeairflow/dreamteller/dreamteller_crawling.py',
    )

    t2b = BashOperator(
        task_id='dreamtellerreviewcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/dreamteller/dreamteller_review_crawling.py',
    )

    t3a = BashOperator(
        task_id='gomongcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/gomong/gomong_crawling.py',
    )

    t3b = BashOperator(
        task_id='gomongreviewcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/gomong/gomong_review_crawling.py',
    )

    t4a = BashOperator(
        task_id='kimsiseoncrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/kimsiseon/kimsiseon_crawling.py',
    )

    t4b = BashOperator(
        task_id='kimsiseonreviewcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/kimsiseon/kimsiseon_review_crawling.py',
    )

    t5a = BashOperator(
        task_id='moviethinkcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/moviethink/moviethink_crawling.py',
    )

    t5b = BashOperator(
        task_id='moviethinkreviewcrawling',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/moviethink/moviethink_review_crawling.py',
    )

    t6 = BashOperator(
        task_id='vod_review_predict',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/vod_review_predict.py',
    )

    t7 = BashOperator(
        task_id='databaseupdate',
        bash_command='python3 /home/ubuntu/airflow/dags/youtubeairflow/database_update.py',
    )

    # 태스크 간의 종속성 설정
    t1a >> t1b >> t2a >> t2b >> t3a >> t3b >> t4a >> t4b >> t5a >> t5b >> t6 >> t7
