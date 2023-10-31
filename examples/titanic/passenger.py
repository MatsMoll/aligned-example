from examples.titanic.source import redis, titanic_source
from aligned import Entity, feature_view
from aligned import Int32, Bool, Float, String
from aligned.schemas.record_coders import JsonRecordCoder
from math import floor, ceil
import polars as pl

@feature_view(
    name="titanic",
    description="Some features from the titanic dataset",
    batch_source=titanic_source,
    stream_source=redis.stream("titanic").with_coder(
        JsonRecordCoder(key="json_data")
    )
)
class TitanicPassenger:
    
    passenger_id = Entity(dtype=Int32())

    # created_at = EventTimestamp()
    
    age = Float()

    
    sibsp = Int32().description("Number of siblings on titanic")
    has_siblings = sibsp > 0
    
    sex = String().accepted_values(["male", "female"])
    is_male, is_female = sex.one_hot_encode(['male', 'female'])

    survived = Bool().description("If the passenger survived").is_required()
    
    name = String()    
    cabin = String()

    # Creates two one hot encoded values
    is_male, is_female = sex.one_hot_encode(['male', 'female'])
    
    # Fill missing values with a constant 0 value
    constant_filled_age = age.fill_na(0)

    # String operations that return a Bool.
    is_mr = name.contains('Mr\.')

    # may not make a lot of sense in this case, but this will
    # encode male as 0 and female as 1
    
    ordinal_sex = sex.ordinal_categories(["male", "female"]).is_required()

    # A lot of the common operations that is expected
    ratio = constant_filled_age / age
    floor_ratio = constant_filled_age // age
    adding = sibsp + age
    greater_than = sibsp > age
    subtracting = sibsp - age
    floored_age = floor(age)
    ceiled_age = ceil(age)
    rounded_age = round(age)
    abs_scaled_age = abs(constant_filled_age)

    # Some logical operators
    inverted_is_mr = ~is_mr
    logical_and = is_mr & survived
    logical_or = is_mr | survived

    age_ratio = age.transform_polars(pl.col("age") / pl.col("age"))

    