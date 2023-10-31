import numpy as np
import asyncio
from aligned import FileSource, PostgreSQLConfig
from dotenv import load_dotenv

async def main():
    from aligned.validation.pandera import PanderaValidator
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from xgboost import XGBRegressor

    load_dotenv()

    # Loading all the compiled features descrived in the /examples folder
    # Can also compile the features on runtime by running `store = await FeatureStore.from_dir(".")`
    store = await FileSource.json_at("feature-store.json").feature_store()

    entity_source = PostgreSQLConfig(env_var="TAXI_DATABASE")
    entites = entity_source.fetch(
        """
        SELECT vendor_id, arrivals.trip_id, departures.pickuped_at as event_timestamp
        FROM arrivals INNER JOIN departures ON arrivals.trip_id = departures.trip_id LIMIT 100
        """
    )
    dataset = await store.model("taxi")\
        .with_target()\
        .features_for(entites)\
        .validate(PanderaValidator())\
        .to_pandas()

    X = dataset.input
    y = dataset.labels
    
    model = XGBRegressor()
    model.fit(dataset.train_input, dataset.train_target)

    predictions = model.predict(dataset.test_input)
    print(f"Mean absolute error: {mean_absolute_error(dataset.test_target, predictions)}")
    print(f"Mean squared error: {mean_squared_error(dataset.test_target, predictions)}")


    psql_config = PostgreSQLConfig(env_var='OTOVO_CLOUD_DB_URL')
    views = store.views_with_config(psql_config)
    validation = await validate_sources_in(views)
    out_of_sync = [name for name, valid in validation.items() if not valid]

    assert len(out_of_sync) == 0, f"""Some views are out of sync: {out_of_sync}.
    Either contact #product-insights so we can update down stream systems, or revert the changes."""


if __name__ == "__main__":
    asyncio.run(main())