
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, desc

def main(spark, input_path_silver, output_path_superset_gold):
    print(f"Membaca data Silver dari: {input_path_silver}")
    df_silver = spark.read.parquet(input_path_silver)
    
    print("Skema data Silver yang diterima di etl_gold_superset.py:")
    df_silver.printSchema()
    df_silver.show(5, truncate=False)

    # --- Agregasi untuk Superset ---
    # PASTIKAN NAMA KOLOM DI BAWAH INI SESUAI DENGAN SKEMA OUTPUT SILVER ANDA
    # Contoh: jika nama kolomnya adalah 'Book-Title' dari books_clean, maka gunakan itu.
    # Jika 'Book-Rating' dari ratings_clean, gunakan itu.

    # Kolom yang mungkin Anda gunakan (cek skema Silver Anda!):
    # Dari books_clean: "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication", "Publisher"
    # Dari ratings_clean: "User-ID", "Book-Rating" (sudah di-cast ke Integer)
    # Dari users_clean: "Location", "Age" (sudah di-cast ke Integer)

    print("Membuat agregasi: Rata-rata rating dan jumlah rating per buku...")
    # Cek apakah kolom yang dibutuhkan ada
    required_cols_agg = ["ISBN", "Book-Title", "Book-Rating"] # Sesuaikan nama ini!
    if not all(c_name in df_silver.columns for c_name in required_cols_agg):
        print(f"Peringatan! Kolom yang dibutuhkan untuk agregasi buku {required_cols_agg} tidak semuanya ada di skema Silver.")
        print(f"Kolom yang tersedia: {df_silver.columns}")
        # Mungkin buat DataFrame kosong atau lewati jika kolom tidak ada
        df_book_summary = spark.createDataFrame(
            [],
            "isbn STRING, book_title STRING, avg_rating DOUBLE, num_ratings LONG" # Skema dummy
        )
    else:
        df_book_summary = df_silver.groupBy(col("ISBN"), col("Book-Title")) \
            .agg(
                avg(col("Book-Rating")).alias("avg_rating"),
                count(col("Book-Rating")).alias("num_ratings")
            ) \
            .orderBy(desc("avg_rating"), desc("num_ratings"))

    print("Hasil agregasi buku untuk Superset:")
    df_book_summary.show(10, truncate=False)

    # Anda bisa menambahkan agregasi lain di sini, misalnya:
    # - Distribusi usia pengguna
    # - Jumlah buku yang dirating per lokasi
    # - dll.

    # --- Simpan ke HDFS Gold (Data Superset) ---
    print(f"Menyimpan data agregat Superset ke: {output_path_superset_gold}")
    df_book_summary.write.mode("overwrite").parquet(output_path_superset_gold)
    print("Data agregat Superset berhasil disimpan.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Silver ke Gold untuk data Superset")
    parser.add_argument("--input_path_silver", required=True, help="Path HDFS ke data Silver (cleaned_joined_data)")
    parser.add_argument("--output_path_superset_gold", required=True, help="Path HDFS untuk output data Superset di Gold")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("BookRec_SilverToGold_Superset_ETL").getOrCreate()

    main(spark, args.input_path_silver, args.output_path_superset_gold)

    spark.stop()