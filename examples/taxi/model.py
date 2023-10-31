from aligned import model_contract, Int32, UUID
from examples.sources import redis, taxi_db
from examples.taxi.arrival import TaxiArrivals
from examples.taxi.departure import TaxiDepartures, TaxiVendor

departures = TaxiDepartures()
arrivals = TaxiArrivals()
vendor = TaxiVendor()

@model_contract(
    name="taxi",
    description="A regression model that predicts the duration of a ride",

    features=[
        departures.day_of_week,
        departures.travel_distance,

        vendor.passenger_hour_variance,
        vendor.passenger_hour_count,
        vendor.passenger_hour_mean,

        vendor.passenger_20_min_variance,
        vendor.passenger_20_min_count,
        vendor.passenger_20_min_mean,

        vendor.mean_passenger_change,
    ],

    predictions_source=taxi_db.table("predicted_trips", mapping_keys={
        "predicted_trips": "predicted_duration"
    }),
    predictions_stream=redis.stream("predicted_trips"),
)
class TaxiModel:

    trip_id = UUID().as_entity()
    vendor_id = Int32().as_entity()

    predicted_duration = arrivals.duration.as_regression_label()\
        .send_ground_truth_event(
            when=arrivals.duration.is_not_null(), 
            sink_to=redis.stream("on_ground_truth")
    )

    model_version = Int32().as_model_version()
