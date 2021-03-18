import time
from datetime import datetime, timedelta
from airflow import DAG
import requests
import airflow
from bs4 import BeautifulSoup
from airflow.hooks.base_hook import BaseHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1)
}
manga_dict = {'17023':'關於我轉生變成史萊姆那檔事', '4740':'進擊的巨人', '7580':'一拳超人', '17332':'輝夜姬想讓人告白', '1128':'海賊王', '13885':'我的英雄學院'}

def check_conn(**context):
   
    for key in manga_dict.keys():
        url = f'https://tw.manhuagui.com/comic/{key}/'
        html_text = requests.get(url, 'html.parser').text
        update_date = datetime.strptime(BeautifulSoup(html_text).find_all('span', {'class':'red'})[-1].text, '%Y-%m-%d').date()
        context['task_instance'].xcom_push(key=f'{key}', value=update_date)


def send_message(**context):
    for key in manga_dict.keys():
        update_date = context['task_instance'].xcom_pull(key=f'{key}')
        if update_date == datetime.now().date():
            SlackAPIPostOperator(
                task_id='send_slack',
                token='xoxb-1672052530309-1696635876802-UASeoGDRIoXxJIuu8Lge3PIK', # Bot User OAuth Access Token
                channel='#manga',
                username='Airflow',
                text=f'{manga_dict[key]} 已更新').execute()
            print(f'{manga_dict[key]} 已更新')
        else:
            SlackAPIPostOperator(
                task_id='send_slack',
                token='xoxb-1672052530309-1696635876802-UASeoGDRIoXxJIuu8Lge3PIK', # Bot User OAuth Access Token
                channel='#manga',
                username='Airflow',
                text=f'{manga_dict[key]} 尚未更新...').execute()
            print(f'{manga_dict[key]} 尚未更新...')
        

with DAG('slack_message', default_args=default_args, schedule_interval='@daily') as dag:

    conn = PythonOperator(
        task_id='check_conn',
        python_callable=check_conn,
        provide_context=True,
        dag=dag
    )

    send_msg = PythonOperator(
        task_id='send_message',
        python_callable=send_message,
        provide_context=True,
        dag=dag
    )

    # work flow define
    conn >> send_msg