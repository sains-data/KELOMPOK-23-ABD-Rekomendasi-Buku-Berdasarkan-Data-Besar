from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType
from pyspark.ml.feature import StringIndexer

spark = SparkSession.builder.appName("Silver_ETL").getOrCreate()

# Load raw CSV dari Bronze (HDFS)
books = spark.read.csv("hdfs://namenode:9000/data-lake/bronze/books", header=True, inferSchema=True)
users = spark.read.csv("hdfs://namenode:9000/data-lake/bronze/users", header=True, inferSchema=True)
ratings = spark.read.csv("hdfs://namenode:9000/data-lake/bronze/ratings", header=True, inferSchema=True)

# Bersihkan data
books_clean = books.dropna(subset=["ISBN", "Book-Title"]).dropDuplicates(["ISBN"])
users_clean = users.dropna(subset=["User-ID"])
ratings_clean = ratings.filter("Book-Rating IS NOT NULL AND Book-Rating >= 0")

# UDF untuk parsing Age
def parse_age(age_str):
    try:
        if age_str is None:
            return None
        if '-' in age_str:
            low, high = age_str.split('-')
            return (int(low) + int(high)) // 2
        return int(age_str)
    except:
        return None

parse_age_udf = udf(parse_age, IntegerType())

users_clean = users_clean.withColumn("age_int", parse_age_udf(users_clean["Age"]))

# StringIndexer untuk User-ID dan ISBN
user_indexer = StringIndexer(inputCol="User-ID", outputCol="user_idx", handleInvalid="skip")
users_indexed = user_indexer.fit(users_clean).transform(users_clean)

isbn_indexer = StringIndexer(inputCol="ISBN", outputCol="book_idx", handleInvalid="skip")
books_indexed = isbn_indexer.fit(books_clean).transform(books_clean)

# Join ratings dengan hasil indexing user dan buku
ratings_indexed = ratings_clean.join(users_indexed.select("User-ID", "user_idx"), on="User-ID", how="inner") \
                               .join(books_indexed.select("ISBN", "book_idx"), on="ISBN", how="inner")

# Simpan ke Silver layer (Parquet)
books_indexed.write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/silver/books")
users_indexed.write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/silver/users")
ratings_indexed.select("user_idx", "book_idx", "Book-Rating").write.mode("overwrite").parquet("hdfs://namenode:9000/data-lake/silver/ratings")
