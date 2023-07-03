from aligned.worker import StreamWorker
from aligned import RedisConfig, FileSource

store = FileSource.json_at("feature-store.json")

worker = (StreamWorker.from_reference(
        store,
        RedisConfig.localhost(),
    )
    .metrics_port(8000)
    .generate_active_learning_dataset()
    .read_from_timestamps({
        "titanic": "$" # From now on and forward in Redis
    })
)