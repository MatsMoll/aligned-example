from aligned import Model, PostgreSQLConfig, RedisConfig, FeatureView, Int32, EventTimestamp, Float, Timestamp, Int64, FileSource
from examples.titanic.passenger import TitanicPassenger
from examples.titanic.source import titanic_source

redis = RedisConfig.localhost()

    # This structure also makes it possible to input the target as an input to another model!!
    # This is awesome
    # Therefore, the model can be an PCA -> Scentence embedding etc.
#  "A model that predicts if passengers will survive. A very basic model, but can do both batch and stream processing, while adding monitoring for better MLOps practices."

class TitanicModel(Model):
    passenger = TitanicPassenger()

    metadata = Model.metadata_with(
        name="titanic",
        description="A model predicting if a passenger will survive on titanic",
        predictions_source=titanic_source,
        features=[
            passenger.constant_filled_age,
            passenger.is_male,
            passenger.is_mr,
            passenger.has_siblings
        ],
    )

    # A condition be needed, and where to sink the ground truth 
    # Since the ground truth is a part of the feature view
    survived = passenger.survived.as_classification_target()\
        .send_ground_truth_event(
            when=passenger.survived.is_not_null(),
            sink_to=redis.stream(topic="passenger_ground_truth"),
    )

    # Drift detection needs. Target distribution (reference dataset), Either input or target features to compare
    # Inference source => At least targets, maybe inputs if stored. Need a new field containing the reference dataset
    # Then a command can check who has everything, and then filter out those that miss enything. 
    # Need to provide clear status logic in the UI if anything is missing tho.


    # Since the granularity if probability is finer then will_survive,
    # Can probability be the only thing being fetched, and then compute will_survive
    # However, the threshold of for our probability will differ based on the cardinality
    # But since `passenger.survived` is a Bool aka will_survive ≈ Target[Bool] can 
    # 
    # However, in reality will it always be a softmax out of all the possible solutions
    # But if multiple cardionality => p_first, p_seconds, pthird = categorical_value.probabililty_of(["first", "second", "third"])
    # Can add a validation rule of sum (probabilites) = 1, even tho data set validation is not supported yet
    # probability = will_survive.probability_of(True)

    # survived_probability = will_survive.probability_for(True)


