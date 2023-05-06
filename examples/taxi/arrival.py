from aligned import FeatureView, EventTimestamp, Int64, UUID
from examples.sources import redis, taxi_db

class TaxiArrivals(FeatureView):

    metadata = FeatureView.metadata_with(
        name="taxi_arrivals",
        description="The arrivals in the taxi data",

        batch_source=taxi_db.table("arrivals"),
        stream_source=redis.stream("arrivals")
    )

    trip_id = UUID().as_entity()

    received_at = EventTimestamp().description(
        "When the arrival records was sent to the server. "
        "It could have been stored on the car for a while"
    )

    duration = Int64()\
        .is_required()\
        .upper_bound(3600 * 4)\
        .description("The duration of the ride")