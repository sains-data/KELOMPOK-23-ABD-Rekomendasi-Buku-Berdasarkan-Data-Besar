from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS

spark = SparkSession.builder.appName("TrainALS").getOrCreate()

# Load data fitur Gold Layer
data = spark.read.parquet("hdfs://namenode:9000/data-lake/gold/features")

train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

als = ALS(
    userCol="user_idx",
    itemCol="book_idx",
    ratingCol="rating",
    rank=10,
    maxIter=20,
    regParam=0.1,
    coldStartStrategy="drop",
    nonnegative=True
)

model = als.fit(train_data)
model.save("hdfs://namenode:9000/models/book_recommendation_als")

spark.stop()
