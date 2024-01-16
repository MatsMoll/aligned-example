from aligned import feature_view, EventTimestamp, Int64, UUID
from examples.sources import redis, taxi_db

@feature_view(
    name="taxi_arrivals",
    description="The arrivals in the taxi data",
    source=taxi_db.table("arrivals"),
    stream_source=redis.stream("arrivals")
)
class TaxiArrivals:

    trip_id = UUID().as_entity()

    received_at = EventTimestamp().description(
        "When the arrival records was sent to the server. "
        "It could have been stored on the car for a while"
    )

    duration = Int64()\
        .is_required()\
        .upper_bound(3600 * 4)\
        .description("The duration of the ride")
