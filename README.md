
# 📚 Book Recommendation System Using Data Lake Architecture

This project presents a scalable book recommendation system built upon a big data processing pipeline using the Medallion architecture (Bronze–Silver–Gold). It utilizes Apache Spark for ETL and model training, Hadoop HDFS for data lake storage, and Apache MLlib for collaborative filtering. This system is designed to demonstrate practical implementation of large-scale data engineering and machine learning workflows using open-source tools.

## 📘 Project Overview

This repository presents an end-to-end implementation of a Book Recommendation System built upon a modern Data Lakehouse architecture. It showcases practical application of data engineering principles, machine learning workflows, and visualization—all orchestrated in a modular and reproducible pipeline.

🔍 **Key Components Included**:

- Data Lake Design 
  Implements the **Medallion Architecture** (Bronze → Silver → Gold) to structure raw, cleaned, and enriched datasets.

- Data Engineering Workflows
  Ingests and processes data using Apache Spark, transforming source CSVs into efficient analytical formats (Parquet/ORC).

- Machine Learning Pipeline
  Builds a **Collaborative Filtering** model (ALS) to generate personalized book recommendations.
---
## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Storage** | HDFS | Distributed file storage |
| **Processing** | Apache Spark | Data processing & ML |
| **Metadata** | Apache Hive | Data warehouse & SQL |
| **Analytics** | PySpark | Data analysis |
| **ML** | Spark MLlib,  | Machine learning |

---

## Architecture and System Component

**Data lake architecture**

![Deskripsi gambar](docs/data-lake-architecture.png)

## 
- Bronze: raw CSV files in HDFS

- Silver: cleaned & joined data in Parquet

- Gold: model output (Top-N recommendations) in ORC/Parquet


###  Dataset Overview

| File | Records | Columns | Deskripsi |
|------|---------|---------|-----------|
| **books.csv** | ~271k | 23 | Informasi detail buku |
| **ratings.csv** | ~1.1M | 3 | Rating pengguna untuk buku |
| **users.csv** | ~278k | 3 | Informasi pengguna |

## 📝 Deployment

### 1. Clone Repositori 

```
git clone https://github.com/sains-data/Sistem-Rekomendasi-Buku.git
```
### 2. Start services
```
docker-compose up -d
```
### 3. Check running container
```
docker ps
```
### 4. Test web UI
| Service           | Function                               | Port | URL  |
| :--------------- | :-------------------------------------------- | :------------ | :--------------------------------- |
| HDFS NameNode    | Melihat status file & direktori (hasil ingest) | `9870`        | `http://localhost:9870`            |
| Spark Master     | Melihat status cluster & daftar aplikasi      | `8080`        | `http://localhost:8080`            |
| Spark Aplikasi   | Detail & progres job Spark (ingest, ML, dll.) | `4040`* | `http://localhost:4040`            |
| HiveServer2      | Menjalankan kueri SQL & melihat sesi          | `10002`       | `http://localhost:10002`           |

### 5. Initialize HDFS

   ```bash
   # Buat direktori HDFS
   docker exec -it namenode hdfs dfs -mkdir -p /user/book-recommendation
   docker exec -it namenode hdfs dfs -mkdir -p /user/book-recommendation/bronze
   docker exec -it namenode hdfs dfs -mkdir -p /user/book-recommendation/silver
   docker exec -it namenode hdfs dfs -mkdir -p /user/book-recommendation/gold
   ```
### 6. Data Ingestion

```bash
# Make script executable
chmod +x scripts/ingest.sh

# Run ingestion
./scripts/ingest.sh
```

### 7. ETL
```bash
# Run ETL script
docker exec -it spark-master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/scripts/etl_bronze_to_silver.py
```

```bash
# Run ETL script
docker exec -it spark-master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/scripts/transform_silver_to_gold.py

```

### 8. Model Training: ALS Algorithm

```
docker exec -it spark-master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/scripts/train_als_model.py
```

### 9.Evaluate Model 
```
# Run model evaluation script
docker exec -it spark-master spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/scripts/evaluate_model.py

```

### 10. Shutting Down the Project

Once you're done working with the pipeline and the services, you can gracefully stop and remove all running containers, networks, and volumes (unless declared as named volumes) using:
```
docker-compose down
```
---
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


