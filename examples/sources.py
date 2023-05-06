from aligned import RedisConfig, PostgreSQLConfig

redis = RedisConfig.localhost()
taxi_db = PostgreSQLConfig("TAXI_DATABASE")