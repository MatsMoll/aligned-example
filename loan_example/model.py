import joblib
from sklearn import tree
from sklearn.exceptions import NotFittedError
from sklearn.preprocessing import OrdinalEncoder
from sklearn.utils.validation import check_is_fitted
from aligned.validation.pandera import PanderaValidator
from aligned.feature_store import ModelFeatureStore
from aligned import FileSource


class CreditScoringModel:

    store: ModelFeatureStore
    classifier: tree.DecisionTreeClassifier
    encoder: OrdinalEncoder
    categorical_features: list[str] 

    def __init__(
        self, 
        store: ModelFeatureStore, 
        classifier: tree.DecisionTreeClassifier = tree.DecisionTreeClassifier(), 
        encoder: OrdinalEncoder = OrdinalEncoder(),
        categorical_features: list[str] = ["state", "city"]
    ):
        self.classifier = classifier
        self.store = store
        self.encoder = encoder
        self.categorical_features = categorical_features

    @staticmethod
    async def load_from_paths(
        model_filename: str = "model.bin", encoder_filename: str = "encoder.bin", 
        feature_store_path: str = "feature-store.json", model_name: str = "credit_scoring"
    ):
        # Load model
        store = await FileSource.json_at(feature_store_path).feature_store()
        classifier = joblib.load(model_filename)
        encoder = joblib.load(encoder_filename)
        categorical_features = ["state", "city"]

        return CreditScoringModel(
            store=store.model(model_name),
            classifier=classifier,
            encoder=encoder,
            categorical_features=categorical_features
        )

    async def train(self, entities):
        training_data = await (
            self.store.with_target()
                .features_for(entities)
                .validate(PanderaValidator())
                .to_pandas()
        )

        self.encoder.fit(training_data.data[self.categorical_features])
        
        # Transform the underlying data into a categorical value
        training_data.data[self.categorical_features] = self.encoder.transform(
            training_data.data[self.categorical_features]
        )
        await FileSource.parquet_at("data/training_dataset.parquet").write_pandas(training_data.data)

        # Select the input and the target features
        self.classifier.fit(
            training_data.input, training_data.target
        )
    
    def dump_model(self, model_path: str, encoder_path: str):
        joblib.dump(self.classifier, model_path)
        joblib.dump(self.encoder, encoder_path)
    
    async def features_for(self, entities): 
        # Get features from Aligned
        job = self.store.features_for(entities)
        # We are only interested in the returned features
        # Therefore, we extract the feature names for the model
        features = job.request_result.feature_columns
        data = await job.to_pandas()

        # Apply ordinal encoding to categorical features
        data[self.categorical_features] = self.encoder.transform(
            data[self.categorical_features]
        )
        return data, features

    async def predict(self, entities, features = None):
        import pandas as pd

        if isinstance(features, pd.DataFrame):
            input_features = features
        else:
            data, feature_columns = await self.features_for(entities)
            input_features = data[feature_columns]

        # Make prediction
        return self.classifier.predict(input_features)

    def with_source(self, source):
        model_name = self.store.model.name
        self.store = self.store.store.with_source(source).model(model_name)
        return self

    def is_model_trained(self):
        try:
            check_is_fitted(self.classifier, "tree_")
        except NotFittedError:
            return False
        return True
