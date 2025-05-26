from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel

import sys

if len(sys.argv) != 2:
    print("Usage: python generate_recommendation.py <user_idx>")
    sys.exit(1)

user_idx = int(sys.argv[1])

spark = SparkSession.builder.appName("GenerateRecommendation").getOrCreate()
model = ALSModel.load("hdfs://namenode:9000/models/book_recommendation_als")

# Generate top 10 rekomendasi buku untuk user_idx tertentu
user_df = spark.createDataFrame([(user_idx,)], ["user_idx"])
recommendations = model.recommendForUserSubset(user_df, 10)

recommendations.show(truncate=False)

spark.stop()
