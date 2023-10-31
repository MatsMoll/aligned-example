from aligned import FeatureView, String, EventTimestamp, Int64, FileSource, RedshiftSQLConfig, feature_view
from datetime import timedelta
import os

if os.getenv("IS_PRODUCTION") != 'true':
    credit_history_source = FileSource.parquet_at("data/credit_history.parquet")
else:
    redshift_config = RedshiftSQLConfig(env_var="CREDIT_DB_URL", schema="spectrum")
    credit_history_source = redshift_config.table("credit_history")


@feature_view(
    name="credit_history",
    description="",
    batch_source=credit_history_source
)
class CreditHistory:
    dob_ssn = String().as_entity().description("Date of birth and last four digits of social security number")

    event_timestamp = EventTimestamp(ttl=timedelta(days=90))

    credit_card_due = Int64()
    mortgage_due = Int64()
    student_loan_due = Int64()
    vehicle_loan_due = Int64()
    hard_pulls = Int64()
    missed_payments_2y = Int64()
    missed_payments_1y = Int64()
    missed_payments_6m = Int64()
    bankruptcies = Int64()

    has_above_5k_credit_debt = credit_card_due > 5000
