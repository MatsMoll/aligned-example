from aligned.compiler.model import Model
from examples.sources import redis, taxi_db
from examples.taxi.arrival import TaxiArrivals
from examples.taxi.departure import TaxiDepartures, TaxiVendor

class TaxiModel(Model):

    departures = TaxiDepartures()
    arrivals = TaxiArrivals()
    vendor = TaxiVendor()

    metadata = Model.metadata_with(
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

        predictions_source=taxi_db.table("predicted_trips"),
        predictions_stream=redis.stream("predicted_trips"),
    )

    duration = arrivals.duration.as_regression_target()\
        .send_ground_truth_event(
            when=arrivals.duration.is_not_null(), 
            sink_to=redis.stream("on_ground_truth")
    )
