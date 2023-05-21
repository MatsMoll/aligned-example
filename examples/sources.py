from aligned import RedisConfig, PostgreSQLConfig, FileSource
from aligned.sources.local import CsvConfig

redis = RedisConfig.localhost()
taxi_db = PostgreSQLConfig("TAXI_DATABASE")
aligned_db = FileSource.csv_at(
    "data/snippets.csv", 
    csv_config=CsvConfig(seperator=";")
)