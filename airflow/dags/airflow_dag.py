from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

with DAG(
    dag_id='book_recommendation_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    bronze_task = BashOperator(
        task_id='bronze_etl',
        bash_command='spark-submit Script/etl-bronze.py'
    )

    silver_task = BashOperator(
        task_id='silver_etl',
        bash_command='spark-submit Script/etl-silver.py'
    )

    gold_task = BashOperator(
        task_id='gold_etl',
        bash_command='spark-submit Script/etl-gold'
    )

    train_task = BashOperator(
        task_id='train_model',
        bash_command='spark-submit Script/train_model.py'
    )

    evaluate_task = BashOperator(
        task_id='evaluate_model',
        bash_command='spark-submit Script/evaluation.py'
    )

    bronze_task >> silver_task >> gold_task >> train_task >> evaluate_task
