
# 📚 Book Recommendation System Using Data Lake Architecture

This project presents a scalable book recommendation system built upon a big data processing pipeline using the Medallion architecture (Bronze–Silver–Gold). It utilizes Apache Spark for ETL and model training, Hadoop HDFS for data lake storage, Apache MLlib for collaborative filtering, and Apache Airflow for workflow orchestration. The final results are visualized through interactive dashboards powered by Apache Superset. This system is designed to demonstrate practical implementation of large-scale data engineering and machine learning workflows using open-source tools.

## 📘 Project Overview

This repository presents an end-to-end implementation of a Book Recommendation System built upon a modern Data Lakehouse architecture. It showcases practical application of data engineering principles, machine learning workflows, and visualization—all orchestrated in a modular and reproducible pipeline.

🔍 **Key Components Included**:

- Data Lake Design 
  Implements the **Medallion Architecture** (Bronze → Silver → Gold) to structure raw, cleaned, and enriched datasets.

- Data Engineering Workflows
  Ingests and processes data using Apache Spark, transforming source CSVs into efficient analytical formats (Parquet/ORC).

- Machine Learning Pipeline
  Builds a **Collaborative Filtering** model (ALS) to generate personalized book recommendations.

- Data Modeling & Storage 
  Incorporates structured table definitions via Hive for easier querying and integration with BI tools.

- Visualization & Insights
  Presents top-N recommendations using Apache Superset dashboards or via programmatic reporting.

---

## 🛠️ Tech Stack

| 🛠️ Tools            | 📂 Kategori          | 🧩 Fungsi                                                                 |
|----------------------|----------------------|--------------------------------------------------------------------------|
| **HDFS**  | Storage              | Menyimpan file mentah (CSV), data terproses (Parquet/ORC)                |
| **Apache Spark**     | Processing Engine    | ETL, cleaning, join, feature engineering, dan training model ALS         |
| **Apache Hive**          | Query Engine / Metadata   | Mendefinisikan tabel eksternal untuk mengakses data pada Gold layer                 |
| **Spark MLlib**      | Machine Learning     | Membangun model rekomendasi berbasis Collaborative Filtering (ALS)      |
| **Apache Airflow**    | Workflow Orchestration   | Menjadwalkan dan mengotomatisasi proses ETL      |
| **Apache Superset**  | Visualization / BI   | Membuat dashboard rekomendasi & analisis visual                          |
| **Apache Ambari** | Cluster Management | Monitoring dan manajemen cluster Hadoop dan komponennya secara visual.             |



## Architecture and System Component

**Data lake architecture**

![Deskripsi gambar](docs/data-lake-architecture.png)


## 
- Bronze: raw CSV files in HDFS

- Silver: cleaned & joined data in Parquet

- Gold: model output (Top-N recommendations) in ORC/Parquet

**System Components**

This project integrates several big data and orchestration tools using Docker. The table below lists the major components, their corresponding container names, and exposed ports:

| **Tools**              | **Container Name**      | **Port (Host:Container)** | **Purpose**                                                 |
|-----------------------|--------------------------|----------------------------|-------------------------------------------------------------|
| **Hadoop NameNode**   | `namenode`               | `9870:9870`, `9000:9000`   | HDFS UI and file system metadata communication              |
| **Hadoop DataNode**   | `datanode`               | `9864:9864`                | HDFS DataNode web interface                                 |
| **Hive Metastore**    | `hive-metastore`         | `9083:9083`                | Central Hive metadata service                               |
| **HiveServer2**       | `hiveserver2`            | `10000:10000`              | SQL engine for querying Hive                                |
| **Spark Master**      | `spark-master`           | `8080:8080`, `7077:7077`   | Spark UI and cluster manager port                           |
| **Spark Worker**      | `spark-worker`           | `8081:8081`                | Spark worker node web UI                                   |
| **PostgreSQL (Hive)** | `postgres-metastore`     | `5432:5432`                | PostgreSQL backend for Hive Metastore                      |
| **PostgreSQL (Airflow)** | `airflow-postgres`   | *(internal only)*          | Metadata database for Airflow                              |
| **Airflow Webserver** | `airflow`                | `8089:8080`                | Web interface for Airflow DAG management                   |
| **Airflow Scheduler** | `airflow-scheduler`      | *(No exposed port)*        | Schedules and triggers DAG executions                      |
| **Airflow Worker**    | `airflow-worker`         | *(No exposed port)*        | Executes DAG tasks                               |
| **Hadoop Client**     | `hadoop-client`          | *(No exposed port)*        | General Hadoop CLI usage (HDFS, YARN, etc.)                |


**Notes:**
- Host ports (on the left) are used to access services via your browser or client tools.
- Services without exposed ports are meant to be accessed internally or via other containers.
- Make sure all ports are available on your system and not used by other services.



**🌐 Accessing Interfaces**

Access these UIs to monitor and interact with system components:

| **Interface**         | **URL**                       | **Notes**                                     |
|-----------------------|-------------------------------|-----------------------------------------------|
| **Airflow UI**        | `http://localhost:8089`       | Login default: `admin` / `admin`               |
| **HDFS UI (NameNode)**| `http://localhost:9870`       | File system browser and HDFS monitoring       |
| **Spark Master UI**   | `http://localhost:8080`       | Spark job status and cluster info             |
| **Spark Worker UI**   | `http://localhost:8081`       | Worker node metrics and logs                  |
| **Superset UI**       | `http://localhost:8088`       | BI dashboards and query visualizations        |

> 📝 If ports above are already in use, edit your `docker-compose.yml` file to map to available host ports.



## 📝 Deployment

1. Clone Repositori 

```
git clone https://github.com/sains-data/Sistem-Rekomendasi-Buku.git
```
2. Start services
```
docker-compose up -d
```
3. Check running container
```
docker ps
```
4. Running the airflow pipeline
- Open your browser and navigate to the Airflow UI at:  
  [http://localhost:8089](http://localhost:8089)

- Login if required (default: `admin` / `admin` — check your config)

- In the DAGs list, locate and **enable** the DAG named:book_recommendation_pipeline


- Click the ▶️ **Trigger DAG** button to run the pipeline manually.

- Monitor the execution via the **Graph View** or **Tree View**, and check task logs if needed.

6. Accessing Book Recommendation Results via Apache Superset

Once the Airflow pipeline `book_recommendation_pipeline` has successfully run and processed the data, the book recommendation results can be explored and visualized using Apache Superset.

- Open your browser and navigate to the Superset UI: `http://localhost:<8081>`
- Log in using your Superset credentials.

7. Shutting Down the Project

Once you're done working with the pipeline and the services, you can gracefully stop and remove all running containers, networks, and volumes (unless declared as named volumes) using:
```
docker-compose down
```


## 🔧 Troubleshooting Guide

This section provides solutions to common issues that may occur while running the Book Recommendation System using Docker, Apache Airflow, and Apache Superset.

---

### 1. Docker & Docker Compose

#### 🚫 Services not running (Exited or Restarting)

```
- Check container logs to identify the error.
- Ensure required ports (e.g., for Airflow, PostgreSQL, Superset) are not in use by other applications.
- Verify that volume mount paths in `docker-compose.yml` are correct and accessible.
- Make sure Docker has sufficient resources (CPU, memory).
- If the issue occurs during the image build process, review the error message for problems in the `Dockerfile` or missing files.
```

---

### 2. Apache Airflow

#### ❌ DAG not showing in Airflow UI

```
- Ensure the DAG file (`.py`) is located in the correct `dags/` directory as defined in `docker-compose.yml`.
- Check the Airflow webserver and scheduler logs for syntax or import errors.
- Wait a few minutes and refresh the UI; DAGs may take time to load.
- Confirm the DAG is toggled **On** in the Airflow UI.
```
#### 🟥 Task failures in a DAG

```
- Review task logs in the Airflow UI for detailed error messages.
- Verify that all required Airflow connections (e.g., database, APIs) are configured correctly.
- Check for bugs or file permission issues in custom scripts.
- Ensure dependent tasks completed successfully.
```
#### 🌐 Webserver or Scheduler unstable or inaccessible

```
- Review logs for both services to identify startup or connectivity issues.
- Ensure the metadata database service (e.g., PostgreSQL) is running and Airflow is correctly configured to connect to it.
```
---

### 3. Recommendation Pipeline Issues

#### 📥 Data ingestion failures
```
- Verify data sources (CSV, API, databases) are accessible from within the container.
- Ensure the data format matches what your ingestion script expects.
- Review task logs in Airflow for specific error messages.
```
#### 🤖 No recommendations generated, or results are incorrect
```
- Check the final pipeline task logs for errors.
- Verify that the output location (database, file path) is writable from Airflow.
- Confirm the schema of the destination table matches the expected output.
- Review the recommendation logic if results are not meaningful.
```
---

### 4. Superset & Database Integration

#### 🔌 Superset can't connect to the database

```
- Confirm the database container is running.
- Check the database connection settings in Superset (hostname, port, username, password, database name).
- Use the service name from `docker-compose.yml` as the database host (e.g., `postgres_results_db`).
- Ensure data is already available from the pipeline run.
- Use the "Test Connection" button in Superset to validate the connection.
```

#### 📊 Superset dashboard or charts display errors
```
- Check and correct the chart or dataset configuration.
- Verify that the referenced tables and columns exist in the database.
- Review Superset logs for additional error details.
```
---

### 🛠️ General Troubleshooting Tips

- Start with the basics: shut everything down, then bring up essential services one at a time to isolate the issue.
- Restart individual services if needed.
- If persistent issues occur due to stale Docker state, consider resetting volumes or unused containers (with caution).
- Ensure your system has sufficient resources (RAM, CPU, disk space), as data processing and analytics can be resource-intensive.

---

> Replace placeholders like `<service_name>` with the actual service names used in your project.

## Struktur Folder

```
book-recommendation-system/
├── README.md
├── airflows
│   ├── dags 
│       └── airflow_dag.py
├── books_data/
│   ├── books.csv
│   ├── users.csv
│   └── ratings.csv
├── Docs/
│   └── data-lake-architecture.png
|   └── README.md
|
├── src/
│   ├── ingest.sh   
│   ├── etl_spark.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── book_recommendation.py
│   └── airflow_dag.py
├── docker-compose.yml
└── requirements.txt
```

--- 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
---

## Contributor

- Mayada (121450145)
- Natasya Ega Lina Marbun (122450024)
- Syalaisha Andini Putriansyah (122450111)
- Anwar Muslim (122450117)


