from aligned import FileSource, RedisConfig

redis = RedisConfig.localhost()

titanic_source = FileSource.csv_at(
    "https://raw.githubusercontent.com/otovo/aligned-example/main/data/titanic.csv", 
    mapping_keys={
        'PassengerId': 'passenger_id',
        'Age': 'age',
        'Name': 'name',
        'Sex': 'sex',
        'Survived': 'survived',
        'SibSp': 'sibsp',
        'Cabin': 'cabin',
})
