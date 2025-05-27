# script/etl_gold_features.py

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer
from pyspark.sql.types import FloatType

def main(spark, input_path_silver, output_path_features_gold):
    print(f"Membaca data Silver dari: {input_path_silver}")
    df_silver = spark.read.parquet(input_path_silver)

    print("Skema data Silver yang diterima di etl_gold_features.py:")
    df_silver.printSchema()
    df_silver.show(5, truncate=False)

    # --- Feature Engineering untuk Model ---
    # PASTIKAN NAMA KOLOM DI BAWAH INI SESUAI DENGAN SKEMA OUTPUT SILVER ANDA
    # Kolom yang dibutuhkan: User-ID, ISBN, Book-Rating

    required_cols_model = ["User-ID", "ISBN", "Book-Rating"] # Sesuaikan nama ini!
    if not all(c_name in df_silver.columns for c_name in required_cols_model):
        print(f"Peringatan! Kolom yang dibutuhkan untuk fitur model {required_cols_model} tidak semuanya ada di skema Silver.")
        print(f"Kolom yang tersedia: {df_silver.columns}")
        # Hentikan proses atau tangani error jika kolom penting tidak ada
        raise ValueError(f"Kolom penting untuk model tidak ditemukan: {required_cols_model}. Kolom tersedia: {df_silver.columns}")

    # 1. Pilih kolom yang relevan untuk model
    df_selected_for_model = df_silver.select(
        col("User-ID"),
        col("ISBN"),
        col("Book-Rating").cast(FloatType()).alias("rating") # Pastikan rating adalah float/double
    )

    # 2. Buat Index Numerik untuk User-ID dan ISBN (karena ALS membutuhkannya)
    print("Membuat index untuk User-ID dan ISBN...")
    user_indexer = StringIndexer(inputCol="User-ID", outputCol="user_index", handleInvalid="skip") # 'skip' akan menghapus baris dengan user_id baru saat transform
    item_indexer = StringIndexer(inputCol="ISBN", outputCol="item_index", handleInvalid="skip") # 'skip' akan menghapus baris dengan isbn baru saat transform
    
    # Fit dan transform
    # Penting: Fit StringIndexer pada data yang akan digunakan untuk training dan evaluasi
    # Jika Anda punya data test terpisah yang di-load di sini, fit pada gabungan train+test
    # atau simpan model StringIndexer untuk digunakan konsisten.
    
    user_indexer_model = user_indexer.fit(df_selected_for_model)
    df_indexed = user_indexer_model.transform(df_selected_for_model)
    
    item_indexer_model = item_indexer.fit(df_indexed)
    df_indexed = item_indexer_model.transform(df_indexed)

    # 3. Pilih kolom akhir untuk input model
    df_model_input = df_indexed.select("user_index", "item_index", "rating")

    # 4. Hapus baris dengan nilai null (mungkin muncul dari handleInvalid='skip' di StringIndexer)
    df_model_input_cleaned = df_model_input.na.drop()

    print("Dataset Fitur Final untuk Model:")
    df_model_input_cleaned.show(10)
    df_model_input_cleaned.printSchema()
    print(f"Jumlah baris setelah pembersihan fitur: {df_model_input_cleaned.count()}")


    # --- Simpan ke HDFS Gold (Features) ---
    print(f"Menyimpan data fitur model ke: {output_path_features_gold}")
    if df_model_input_cleaned.count() > 0:
        df_model_input_cleaned.write.mode("overwrite").parquet(output_path_features_gold)
        print("Data fitur model berhasil disimpan.")
    else:
        print("Tidak ada data fitur yang valid untuk disimpan setelah pembersihan.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Silver ke Gold untuk fitur model rekomendasi")
    parser.add_argument("--input_path_silver", required=True, help="Path HDFS ke data Silver (cleaned_joined_data)")
    parser.add_argument("--output_path_features_gold", required=True, help="Path HDFS untuk output fitur model di Gold")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("BookRec_SilverToGold_Features_ETL").getOrCreate()

    main(spark, args.input_path_silver, args.output_path_features_gold)

    spark.stop()