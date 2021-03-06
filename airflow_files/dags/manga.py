import time
from datetime import datetime, timedelta
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021, 1, 30),
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}


# SLACK_CONN_ID = 'slack'
# slack_msg = 'testing'
# slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password

# with DAG('comic_app', default_args=default_args) as dag:

#     send_notification = SlackWebhookOperator(
#         task_id='send_message',
#         http_conn_id='slack',
#         webhook_token=slack_webhook_token,
#         username='airflow',
#         message=slack_msg
#     )

def process_metadata(mode, **context):
    if mode == 'read':
        print("取得使用者的閱讀紀錄")
    elif mode == 'write':
        print("更新閱讀紀錄")


def check_comic_info(**context):
    all_comic_info = context['task_instance'].xcom_pull(task_ids='get_read_history')
    print("去漫畫網站看有沒有新的章節")

    anything_new = time.time() % 2 > 1
    return anything_new, all_comic_info


def decide_what_to_do(**context):
    anything_new, all_comic_info = context['task_instance'].xcom_pull(task_ids='check_comic_info')

    print("跟紀錄比較，有沒有新連載？")
    if anything_new:
        return 'yes_generate_notification'
    else:
        return 'no_do_nothing'


def generate_message(**context):
    _, all_comic_info = context['task_instance'].xcom_pull(task_ids='check_comic_info')
    print("產生要寄給 Slack 的訊息內容並存成檔案")


with DAG('comic_app_v2', default_args=default_args) as dag:

    get_read_history = PythonOperator(
        task_id='get_read_history',
        python_callable=process_metadata,
        op_args=['read']
    )

    check_comic_info = PythonOperator(
        task_id='check_comic_info',
        python_callable=check_comic_info,
        provide_context=True
    )

    decide_what_to_do = BranchPythonOperator(
        task_id='new_comic_available',
        python_callable=decide_what_to_do,
        provide_context=True
    )

    update_read_history = PythonOperator(
        task_id='update_read_history',
        python_callable=process_metadata,
        op_args=['write'],
        provide_context=True
    )

    generate_notification = PythonOperator(
        task_id='yes_generate_notification',
        python_callable=generate_message,
        provide_context=True
    )

    send_notification = SlackAPIPostOperator(
        task_id='send_notification',
        token="xoxb-1672052530309-1696635876802-UASeoGDRIoXxJIuu8Lge3PIK",
        channel='#manga',
        text="海賊王有新番了!",
        icon_url='http://airbnb.io/img/projects/airflow3.png'
    )

    do_nothing = DummyOperator(task_id='no_do_nothing')

    # define workflow
    get_read_history >> check_comic_info >> decide_what_to_do

    decide_what_to_do >> generate_notification
    decide_what_to_do >> do_nothing

    generate_notification >> send_notification >> update_read_history