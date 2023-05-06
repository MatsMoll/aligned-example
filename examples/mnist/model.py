from examples.mnist.features import MnistFeature
from aligned import Model

class Mnist(Model):

    data = MnistFeature()

    metadata = Model.metadata_with(
        "mnist",
        description="A model that detects handwritten images",
        features=[
            data.grayscale_image
        ]
    )

    number = data.label.as_classification_target()
