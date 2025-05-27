from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash_operator import BashOperator 
from airflow.operators.dummy_operator import DummyOperator 

# --- Konfigurasi Path (Sesuaikan dengan lingkungan Anda di dalam Docker) ---
# Path ini adalah path di dalam container Spark/Airflow
HDFS_BASE_PATH = "/user/airflow/medallion/book_recommendation" # Base path HDFS
HDFS_BRONZE_PATH = f"{HDFS_BASE_PATH}/bronze"
HDFS_SILVER_PATH = f"{HDFS_BASE_PATH}/silver"
HDFS_GOLD_PATH = f"{HDFS_BASE_PATH}/gold"
HDFS_MODEL_PATH = f"{HDFS_BASE_PATH}/models"

# Path skrip Spark di dalam container (di-mount dari ./spark_apps)
SPARK_SCRIPT_PATH = "/opt/spark_apps"

# Path data CSV di dalam container (di-mount dari ./data_source)
LOCAL_DATA_PATH = "/opt/data_source"

# Nama file dataset
BOOKS_CSV = "books.csv"
RATINGS_CSV = "ratings.csv"
USERS_CSV = "users.csv"

# Detail untuk spark-submit
SPARK_MASTER_URL = "spark://spark-master:7077" # Sesuai nama service di docker-compose

# Tanggal mulai DAG
YESTERDAY = pendulum.yesterday("Asia/Jakarta").subtract(days=1) # Agar bisa langsung jalan

with DAG(
    dag_id="book_recommendation_medallion_pipeline",
    start_date=YESTERDAY,
    schedule_interval="@daily", # Atau None untuk manual trigger
    catchup=False,
    tags=["book_recommendation", "medallion", "spark", "ml"],
    doc_md="""
    ### Pipeline Sistem Rekomendasi Buku dengan Arsitektur Medallion
    Mengelola ETL data buku, rating, pengguna, melatih model, dan menyiapkan data untuk visualisasi.
    """,
) as dag:
    start_pipeline = DummyOperator(task_id="start_pipeline")

    # --- 🥉 Lapisan Bronze: Ingest Data Mentah ---
    # Task 1: Membuat direktori di HDFS jika belum ada
    create_hdfs_bronze_dirs = BashOperator(
        task_id="create_hdfs_bronze_directories",
        bash_command=(
            f"hdfs dfs -mkdir -p {HDFS_BRONZE_PATH}/books && "
            f"hdfs dfs -mkdir -p {HDFS_BRONZE_PATH}/ratings && "
            f"hdfs dfs -mkdir -p {HDFS_BRONZE_PATH}/users"
        ),
    )

    # Task 2: Ingest books.csv ke HDFS Bronze
    ingest_books_to_bronze = BashOperator(
        task_id="ingest_books_to_bronze",
        bash_command=f"hdfs dfs -put -f {LOCAL_DATA_PATH}/{BOOKS_CSV} {HDFS_BRONZE_PATH}/books/{BOOKS_CSV}",
    )

    # Task 3: Ingest ratings.csv ke HDFS Bronze
    ingest_ratings_to_bronze = BashOperator(
        task_id="ingest_ratings_to_bronze",
        bash_command=f"hdfs dfs -put -f {LOCAL_DATA_PATH}/{RATINGS_CSV} {HDFS_BRONZE_PATH}/ratings/{RATINGS_CSV}",
    )

    # Task 4: Ingest users.csv ke HDFS Bronze
    ingest_users_to_bronze = BashOperator(
        task_id="ingest_users_to_bronze",
        bash_command=f"hdfs dfs -put -f {LOCAL_DATA_PATH}/{USERS_CSV} {HDFS_BRONZE_PATH}/users/{USERS_CSV}",
    )

    # --- 🥈 Lapisan Silver: Data Bersih dan Terstruktur ---
    # Task 5: Membuat direktori HDFS Silver
    create_hdfs_silver_dir = BashOperator(
        task_id="create_hdfs_silver_directory",
        bash_command=f"hdfs dfs -mkdir -p {HDFS_SILVER_PATH}/cleaned_data",
    )

    # Task 6: Jalankan Spark job untuk proses Bronze ke Silver
    process_bronze_to_silver = BashOperator(
        task_id="process_bronze_to_silver_spark",
        bash_command=(
            f"spark-submit --master {SPARK_MASTER_URL} "
            f"{SPARK_SCRIPT_PATH}/etl_silver.py " # Nama skrip Spark Anda
            f"--input_books_path {HDFS_BRONZE_PATH}/books/{BOOKS_CSV} "
            f"--input_ratings_path {HDFS_BRONZE_PATH}/ratings/{RATINGS_CSV} "
            f"--input_users_path {HDFS_BRONZE_PATH}/users/{USERS_CSV} "
            f"--output_path {HDFS_SILVER_PATH}/cleaned_data"
        ),
    )

    # --- 🥇 Lapisan Gold: Data Siap Analisis dan Fitur Model ---
    # Task 7: Membuat direktori HDFS Gold
    create_hdfs_gold_dirs = BashOperator(
        task_id="create_hdfs_gold_directories",
        bash_command=(
            f"hdfs dfs -mkdir -p {HDFS_GOLD_PATH}/features_for_model && "
            f"hdfs dfs -mkdir -p {HDFS_GOLD_PATH}/data_for_superset"
        ),
    )

    # Task 8: Jalankan Spark job untuk proses Silver ke Gold (Fitur Model)
    process_silver_to_gold_features = BashOperator(
        task_id="process_silver_to_gold_features_spark",
        bash_command=(
            f"spark-submit --master {SPARK_MASTER_URL} "
            f"{SPARK_SCRIPT_PATH}/etl_gold_features.py " # Nama skrip Spark Anda
            f"--input_path {HDFS_SILVER_PATH}/cleaned_data "
            f"--output_features_path {HDFS_GOLD_PATH}/features_for_model"
        ),
    )

    # Task 9: Jalankan Spark job untuk proses Silver ke Gold (Data Superset)
    process_silver_to_gold_superset = BashOperator(
        task_id="process_silver_to_gold_superset_spark",
        bash_command=(
            f"spark-submit --master {SPARK_MASTER_URL} "
            f"{SPARK_SCRIPT_PATH}/etl_gold_superset.py " # Nama skrip Spark Anda
            f"--input_path {HDFS_SILVER_PATH}/cleaned_data "
            f"--output_superset_path {HDFS_GOLD_PATH}/data_for_superset"
        ),
    )

    # --- 🤖 Pelatihan Model (MLlib Collaborative Filtering) ---
    # Task 10: Membuat direktori HDFS untuk Model
    create_hdfs_model_dir = BashOperator(
        task_id="create_hdfs_model_directory",
        bash_command=f"hdfs dfs -mkdir -p {HDFS_MODEL_PATH}",
    )

    # Task 11: Jalankan Spark job untuk melatih model rekomendasi
    train_recommendation_model = BashOperator(
        task_id="train_recommendation_model_spark",
        bash_command=(
            f"spark-submit --master {SPARK_MASTER_URL} "
            f"{SPARK_SCRIPT_PATH}/train_model.py " # Nama skrip Spark Anda
            f"--input_features_path {HDFS_GOLD_PATH}/features_for_model "
            f"--model_output_path {HDFS_MODEL_PATH}/als_model_$(date +%Y%m%d_%H%M%S)"
        ),
    )

    # --- 🏁 Akhir Pipeline ---
    data_for_superset_ready = DummyOperator(task_id="data_for_superset_ready")
    model_trained = DummyOperator(task_id="model_trained")
    end_pipeline = DummyOperator(task_id="end_pipeline")

    # --- Mendefinisikan Alur (Dependencies) ---
    start_pipeline >> create_hdfs_bronze_dirs
    create_hdfs_bronze_dirs >> [ingest_books_to_bronze, ingest_ratings_to_bronze, ingest_users_to_bronze]

    [ingest_books_to_bronze, ingest_ratings_to_bronze, ingest_users_to_bronze] >> create_hdfs_silver_dir >> process_bronze_to_silver

    process_bronze_to_silver >> create_hdfs_gold_dirs
    create_hdfs_gold_dirs >> process_silver_to_gold_features
    create_hdfs_gold_dirs >> process_silver_to_gold_superset

    process_silver_to_gold_features >> create_hdfs_model_dir >> train_recommendation_model >> model_trained
    process_silver_to_gold_superset >> data_for_superset_ready

    [model_trained, data_for_superset_ready] >> end_pipeline