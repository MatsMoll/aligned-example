from examples.mnist.features import MnistFeature
from aligned import model_contract

data = MnistFeature()

@model_contract(
    "mnist",
    description="A model that detects handwritten images",
    features=[
        data.grayscale_image
    ]
)
class Mnist:
    number = data.label.as_classification_label()
