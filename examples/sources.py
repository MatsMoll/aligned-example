from aligned import RedisConfig, PostgreSQLConfig, FileSource
from aligned.sources.local import CsvConfig

redis = RedisConfig.localhost()
taxi_db = PostgreSQLConfig("TAXI_DATABASE")

data_dir = FileSource.directory("https://raw.githubusercontent.com/MatsMoll/aligned-example/main/data/")
aligned_db = data_dir.csv_at("snippets.csv", csv_config=CsvConfig(seperator=";")
)
