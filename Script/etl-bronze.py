from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Bronze_ETL").getOrCreate()

# Load CSV mentah dari local atau sumber lain
books_raw = spark.read.csv("books_data/books.csv", header=True, inferSchema=True)
users_raw = spark.read.csv("books_data/users.csv", header=True, inferSchema=True)
ratings_raw = spark.read.csv("books_data/ratings.csv", header=True, inferSchema=True)

# Simpan data mentah ke bronze layer di HDFS (atau sesuai sistem file)
books_raw.write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/bronze/books")
users_raw.write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/bronze/users")
ratings_raw.write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/bronze/ratings")

spark.stop()
