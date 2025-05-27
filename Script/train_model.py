# script/train_model.py

import argparse
from pyspark.sql import SparkSession
# Ini dia yang penting untuk ALS:
from pyspark.ml.recommendation import ALS # 👈
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col

def main(spark, input_features_path, model_output_path):
    print(f"Membaca data fitur dari: {input_features_path}")
    # df_model_input akan berisi kolom: user_index, item_index, rating
    df_model_input = spark.read.parquet(input_features_path) 
    df_model_input.show(5)
    df_model_input.printSchema()

    # ... (pengecekan kolom) ...

    # --- Pelatihan Model ALS ---
    (training_data, test_data) = df_model_input.randomSplit([0.8, 0.2], seed=42)

    print("Memulai pelatihan model ALS...")
    # Konfigurasi ALS (sesuaikan hyperparameter ini)
    als = ALS(  # 👈 Di sinilah objek ALS dibuat
        maxIter=10,             
        regParam=0.1,           
        userCol="user_index",   # Kolom input untuk user (hasil StringIndexer)
        itemCol="item_index",   # Kolom input untuk item (hasil StringIndexer)
        ratingCol="rating",     # Kolom input untuk rating
        coldStartStrategy="drop", 
        nonnegative=True          
    )

    model = als.fit(training_data) # 👈 Model ALS dilatih di sini
    print("Pelatihan model selesai.")

    # ... (Evaluasi Model) ...

    # --- Simpan Model ---
    print(f"Menyimpan model ke: {model_output_path}")
    model.write().overwrite().save(model_output_path) # 👈 Model ALS disimpan
    print(f"Model berhasil disimpan di {model_output_path}")

    # ... (Contoh membuat rekomendasi) ...

# ... (bagian if __name__ == "__main__":) ...