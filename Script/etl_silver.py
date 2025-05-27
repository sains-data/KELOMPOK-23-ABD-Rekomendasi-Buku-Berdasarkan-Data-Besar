# spark_apps/etl_silver.py (Revisi)

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, when # Import 'when'
from pyspark.sql.types import IntegerType
# StringIndexer tidak lagi digunakan di Silver jika tujuan utamanya adalah dataset gabungan bersih.
# Indexing lebih cocok di Gold untuk persiapan model.

def parse_age_udf_func(age_str): # Ubah nama fungsi agar lebih jelas
    """UDF untuk parsing Age, menangani rentang dan nilai non-numerik."""
    try:
        if age_str is None:
            return None
        if '-' in age_str: # Menangani rentang usia, misal "25-34"
            low, high = map(int, age_str.split('-')) # Konversi ke int langsung
            return (low + high) // 2
        return int(age_str)
    except (ValueError, TypeError): # Lebih spesifik menangani error konversi
        return None

def main(spark, input_books_path, input_ratings_path, input_users_path, output_path_silver_cleaned):
    print(f"Memulai ETL Bronze ke Silver...")
    print(f"Membaca books dari: {input_books_path}")
    books = spark.read.csv(input_books_path, header=True, inferSchema=True, sep=";") # Sesuaikan separator jika perlu
    
    print(f"Membaca users dari: {input_users_path}")
    users = spark.read.csv(input_users_path, header=True, inferSchema=True, sep=";") # Sesuaikan separator jika perlu
    
    print(f"Membaca ratings dari: {input_ratings_path}")
    ratings = spark.read.csv(input_ratings_path, header=True, inferSchema=True, sep=";") # Sesuaikan separator jika perlu

    # --- Pembersihan Data ---
    print("Membersihkan data books...")
    # Menghapus duplikat ISBN, memilih yang pertama muncul (bisa disesuaikan jika ada logika lain)
    # Pastikan "ISBN" dan "Book-Title" adalah nama kolom yang benar.
    books_clean = books.dropna(subset=["ISBN", "Book-Title"]) \
                       .dropDuplicates(["ISBN"]) 
    books_clean.printSchema()
    books_clean.show(5, truncate=False)

    print("Membersihkan data users...")
    # Pastikan "User-ID" adalah nama kolom yang benar.
    users_clean = users.dropna(subset=["User-ID"]) \
                       .dropDuplicates(["User-ID"]) # Tambahkan dropDuplicates untuk User-ID

    # Registrasi dan penggunaan UDF untuk Age
    parse_age_udf = udf(parse_age_udf_func, IntegerType())
    users_clean = users_clean.withColumn("age_cleaned", parse_age_udf(col("Age"))) \
                             .drop("Age") \
                             .withColumnRenamed("age_cleaned", "Age") # Ganti nama kembali ke "Age"
    users_clean.printSchema()
    users_clean.show(5, truncate=False)
    
    print("Membersihkan data ratings...")
    # Pastikan "Book-Rating" adalah nama kolom yang benar.
    # Lebih baik cast ke tipe numerik dan filter, daripada filter string
    ratings_clean = ratings.withColumn("Book-Rating_temp", col("Book-Rating").cast(IntegerType())) \
                           .filter(col("Book-Rating_temp").isNotNull() & (col("Book-Rating_temp") >= 0)) \
                           .drop("Book-Rating") \
                           .withColumnRenamed("Book-Rating_temp", "Book-Rating")
    ratings_clean.printSchema()
    ratings_clean.show(5, truncate=False)
# --- Penggabungan Data (Join) ---
    # Tujuan utama Silver adalah dataset gabungan yang bersih.
    print("Menggabungkan dataset...")
    # Pastikan nama kolom untuk join ("User-ID", "ISBN") sudah benar.
    # Jika nama kolom di CSV asli menggunakan tanda hubung, pastikan di DataFrame Spark juga sama
    # atau sudah Anda ganti namanya saat pembersihan.
    silver_df = ratings_clean.join(users_clean, ratings_clean["User-ID"] == users_clean["User-ID"], "inner") \
                             .join(books_clean, ratings_clean["ISBN"] == books_clean["ISBN"], "inner") \
                             .drop(users_clean["User-ID"]) \
                             .drop(books_clean["ISBN"])      # Hapus kolom ISBN duplikat dari books_clean
    
    # Menyimpan semua kolom hasil join
    silver_df_final = silver_df

    print("Skema dataset Silver final setelah join:")
    silver_df_final.printSchema()
    silver_df_final.show(5, truncate=False)

    # --- Simpan ke Silver Layer (Parquet) ---
    # Hanya satu dataset gabungan yang disimpan di Silver.
    print(f"Menyimpan dataset Silver gabungan ke: {output_path_silver_cleaned}")
    silver_df_final.write.mode("overwrite").parquet(output_path_silver_cleaned)
    print("Dataset Silver berhasil disimpan.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Bronze ke Silver untuk data rekomendasi buku")
    # Argumen input path harus sesuai dengan yang dikirim dari Airflow DAG
    parser.add_argument("--input_books_path", required=True, help="Path HDFS ke books.csv di Bronze")
    parser.add_argument("--input_ratings_path", required=True, help="Path HDFS ke ratings.csv di Bronze")
    parser.add_argument("--input_users_path", required=True, help="Path HDFS ke users.csv di Bronze")
    # Argumen output path harus sesuai dengan yang dikirim dari Airflow DAG
    parser.add_argument("--output_path_silver_cleaned", required=True, help="Path HDFS untuk output Silver yang sudah dibersihkan dan digabung")
    
    args = parser.parse_args()

    spark = SparkSession.builder.appName("BookRec_BronzeToSilver_ETL").getOrCreate()

    main(spark, 
         args.input_books_path, 
         args.input_ratings_path, 
         args.input_users_path, 
         args.output_path_silver_cleaned)

    spark.stop()