from aligned import feature_view, EventTimestamp, Float, UUID, Int32, combined_feature_view
from aligned.compiler.feature_factory import Coordinate
from examples.sources import redis, taxi_db


@feature_view(
    name="taxi_departures",
    description="Features related to the departure of a taxi ride",

    batch_source=taxi_db.table("departures"),
    stream_source=redis.stream("departures"),
)
class TaxiDepartures:
    trip_id = UUID().as_entity()

    pickuped_at = EventTimestamp()

    number_of_passengers = Int32()

    dropoff_latitude = Float().is_required()
    dropoff_longitude = Float().is_required()

    pickup_latitude = Float().is_required()
    pickup_longitude = Float().is_required()

    dropoff_coordinate = Coordinate(dropoff_latitude, dropoff_longitude)
    pickup_coordinate = Coordinate(pickup_latitude, pickup_longitude)

    travel_distance = dropoff_coordinate.eucledian_distance(pickup_coordinate).lower_bound(0)

    day_of_week = pickuped_at.date_component("day").description("The day in the month")



@feature_view(
    name="taxi_vendor",
    description="Features realated to the taxi vendor",

    batch_source=taxi_db.table("departures", mapping_keys={
        "passenger_count": "number_of_passengers"
    }),
    stream_source=redis.stream("departures"),
)
class TaxiVendor:

    vendor_id = Int32().as_entity()
    pickuped_at = EventTimestamp()

    number_of_passengers = Int32().is_required().lower_bound(0)

    passenger_hour_aggregate = number_of_passengers.aggregate().over(hours=1)
    passenger_20_min_aggregate = number_of_passengers.aggregate().over(minutes=20)

    passenger_hour_mean = passenger_hour_aggregate.mean()
    passenger_20_min_mean = passenger_20_min_aggregate.mean()

    passenger_hour_sum = passenger_hour_aggregate.sum()
    passenger_hour_variance = passenger_hour_aggregate.variance()
    passenger_hour_count = passenger_hour_aggregate.count()


    passenger_20_min_sum = passenger_20_min_aggregate.sum()
    passenger_20_min_variance = passenger_20_min_aggregate.variance()
    passenger_20_min_count = passenger_20_min_aggregate.count()

    mean_passenger_change = passenger_20_min_mean - passenger_hour_mean
