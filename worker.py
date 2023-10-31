from aligned.worker import StreamWorker
from aligned import RedisConfig, FileSource

store = FileSource.json_at("feature-store.json")

worker = (StreamWorker.from_reference(
        store,
        RedisConfig.localhost(),
    )
    .expose_metrics_at(8000)
    .read_from_timestamps({
        "titanic": "$", # From now on and forward in Redis
        "taxi_arrivals": "0-0", # From the begining of the stream
    })
)
