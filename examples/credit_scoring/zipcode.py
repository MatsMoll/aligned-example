from aligned import String, Int64, EventTimestamp, FileSource, RedshiftSQLConfig, KafkaConfig, feature_view
from examples.sources import data_dir
from datetime import timedelta
import os 

kafka_server = KafkaConfig("KAFKA_SERVER")

if os.getenv("IS_PRODUCTION") != 'true':
    zipcode_source = data_dir.parquet_at("zipcode_table.parquet")
    credit_history_source = data_dir.parquet_at("credit_history.parquet")
else:
    redshift_config = RedshiftSQLConfig(env_var="CREDIT_DB_URL", schema="spectrum")

    zipcode_source = redshift_config.table("zipcode_features")
    credit_history_source = redshift_config.table("credit_history")


@feature_view(
    name="zipcode_features",
    description="",
    source=zipcode_source,
    # stream_source=kafka_server.topic("zipcode_features")
)
class Zipcode:

    zipcode = Int64().as_entity()

    event_timestamp = EventTimestamp(ttl=timedelta(days=3650))

    city = String()
    state = String()
    location_type = String()
    tax_returns_filed = Int64()
    population = Int64()
    total_wages = Int64()

    is_primary_location = location_type == "PRIMARY"

