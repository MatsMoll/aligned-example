from aligned import RedisConfig, FileSource
from aligned.schemas.repo_definition import FeatureServer

store = FileSource.json_at("feature-store.json")

server = FeatureServer.from_reference(
    store,
    RedisConfig.localhost().online_source()
)