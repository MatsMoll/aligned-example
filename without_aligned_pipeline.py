import polars as pl
import pandas as pd
from pandera import DataFrameSchema, Check, Column
from pandera.errors import SchemaError
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from dotenv import load_dotenv
from os import environ

def load_data() -> pd.DataFrame:
    return pl.read_sql(
        """
WITH entities (
    vendor_id, trip_id, event_timestamp, row_id
) AS (
    SELECT vendor_id, trip_id, event_timestamp, ROW_NUMBER() OVER (ORDER BY trip_id) AS row_id FROM (SELECT vendor_id, arrivals.trip_id, departures.pickuped_at as event_timestamp FROM arrivals INNER JOIN departures ON arrivals.trip_id = departures.trip_id LIMIT 100) AS entities
),
taxi_departures_cte AS (
    SELECT DISTINCT ON (entities.row_id) pickuped_at, entities.trip_id, dropoff_longitude, entities.row_id, dropoff_latitude, pickup_longitude, pickup_latitude
    FROM entities
    LEFT JOIN "departures" ta ON ta."trip_id" = entities.trip_id AND entities.event_timestamp >= ta.pickuped_at
    ORDER BY entities.row_id, pickuped_at DESC
    ),
taxi_arrivalstarget_cte AS (

    SELECT DISTINCT ON (entities.row_id) entities.trip_id, entities.row_id, duration
    FROM entities
    LEFT JOIN "arrivals" ta ON ta."trip_id" = entities.trip_id
    ORDER BY entities.row_id
    ),
taxi_vendor_agg_3600_cte AS (

    SELECT AVG(number_of_passengers) AS "passenger_hour_mean", entities.row_id, COUNT(number_of_passengers) AS "passenger_hour_count", variance(number_of_passengers) AS "passenger_hour_variance"
    FROM (
    SELECT entities.*, passenger_count AS "number_of_passengers"
    FROM entities
    LEFT JOIN "departures" ta ON ta."vendor_id" = entities.vendor_id AND ta.pickuped_at BETWEEN entities.event_timestamp - interval '3600 seconds' AND entities.event_timestamp
    ) as entities
    GROUP BY row_id
    ),
taxi_vendor_agg_1200_cte AS (
    
SELECT 
    AVG(number_of_passengers) AS "passenger_20_min_mean", 
    COUNT(number_of_passengers) AS "passenger_20_min_count", 
    entities.row_id
FROM (
    SELECT passenger_count AS "number_of_passengers", entities.*
    FROM entities
    LEFT JOIN "departures" ta ON ta."vendor_id" = entities.vendor_id 
    AND ta.pickuped_at BETWEEN entities.event_timestamp - interval '1200 seconds' AND entities.event_timestamp
) as entities
GROUP BY row_id
    )
SELECT 
    taxi_departures_cte.dropoff_longitude, passenger_hour_mean, 
    taxi_departures_cte.pickuped_at, passenger_20_min_mean, passenger_20_min_count, entities.vendor_id, entities.trip_id, taxi_departures_cte.pickup_latitude, taxi_arrivalstarget_cte.duration, 
    event_timestamp, entities.row_id, passenger_hour_variance, passenger_hour_count, taxi_departures_cte.pickup_longitude, passenger_20_min_variance, taxi_departures_cte.dropoff_latitude
FROM entities
INNER JOIN taxi_departures_cte ON taxi_departures_cte.row_id = entities.row_id
    INNER JOIN taxi_arrivalstarget_cte ON taxi_arrivalstarget_cte.row_id = entities.row_id
    INNER JOIN taxi_vendor_agg_3600_cte ON taxi_vendor_agg_3600_cte.row_id = entities.row_id
    INNER JOIN taxi_vendor_agg_1200_cte ON taxi_vendor_agg_1200_cte.row_id = entities.row_id
""", 
        environ["TAXI_DATABASE"]
    ).to_pandas()


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    # Eucledian distance
    df["lat_diff"] = (df["pickup_latitude"] - df["dropoff_latitude"]) ** 2
    df["long_diff"] = (df["pickup_longitude"] - df["dropoff_longitude"]) ** 2
    df["travel_distance"] = (df["lat_diff"] + df["long_diff"]) ** 0.5

    # Day of the week
    df["day_of_week"] = df["pickuped_at"].dt.day

    # Difference in passenger mean value between 20 min and 1 hour
    df["mean_passenger_change"] = df["passenger_20_min_mean"] - df["passenger_hour_mean"]
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    schema = DataFrameSchema(columns={
        "dropoff_latitude": Column(float, nullable=True),
        "dropoff_longitude": Column(float, nullable=True),
        "pickup_latitude": Column(float, nullable=True),
        "pickup_longitude": Column(float, nullable=True),
        "passenger_hour_mean": Column(float, nullable=True),
        "passenger_hour_count": Column(int, nullable=True),
        "passenger_hour_variance": Column(float, nullable=True),
        "passenger_20_min_mean": Column(float, nullable=True),
        "passenger_20_min_count": Column(int, nullable=True),
        "passenger_20_min_variance": Column(float, nullable=True),
        "duration": Column(int, nullable=False, required=True, checks=[Check.less_than(3600 * 4)]),
        "lat_diff": Column(float, nullable=True),
        "long_diff": Column(float, nullable=True),
        "travel_distance": Column(float, checks=[Check.greater_than(0)], nullable=True),
        "day_of_week": Column(int, nullable=True),
    })

    try:
        return schema.validate(df)
    except SchemaError as error:
        # Will only return one error at a time, so will remove
        # errors and then run it recrusive

        if error.failure_cases.shape[0] == df.shape[0]:
            raise ValueError('Validation is removing all the data.')

        if error.failure_cases['index'].iloc[0] is None:
            raise ValueError(error)

        return validate_data(
            df.loc[df.index.delete(error.failure_cases['index'])].reset_index()
        )

def main():
    load_dotenv()
    data = load_data()
    data = process_data(data)
    data = validate_data(data)
    
    expected_features = [
        "day_of_week",
        "mean_passenger_change", 
        "passenger_20_min_count", 
        "passenger_20_min_mean", 
        "passenger_20_min_variance", 
        "passenger_hour_count", 
        "passenger_hour_mean", 
        "passenger_hour_variance", 
        "travel_distance"
    ]
    target_feature = ["duration"]

    data = data.sort_values(by="event_timestamp", ascending=True)

    tscv = TimeSeriesSplit(max_train_size=80, n_splits=2, test_size=20)

    for i, (train_index, test_index) in enumerate(tscv.split(data)):
        if i != 1:
            continue
        train_data = data.iloc[train_index][expected_features]
        test_data = data.iloc[test_index][expected_features]

        train_target = data.iloc[train_index][target_feature]
        test_target = data.iloc[test_index][target_feature]

        model = XGBRegressor()
        model.fit(train_data, train_target)

        predictions = model.predict(test_data)
        print(f"Mean absolute error: {mean_absolute_error(test_target, predictions)}")
        print(f"Mean squared error: {mean_squared_error(test_target, predictions)}")


if __name__ == "__main__":
    main()