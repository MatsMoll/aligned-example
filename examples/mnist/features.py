from aligned import FeatureView, Int32
from aligned.compiler.feature_factory import ImageUrl
from examples.mnist.source import mnist_source

class MnistFeature(FeatureView):

    metadata = FeatureView.metadata_with(
        "mnist",
        "Features desrcribing the mnist features",
        mnist_source
    )

    id = Int32().as_entity()
    image_url = ImageUrl()

    image = image_url.load_image()
    grayscale_image = image.to_grayscale()

    label = Int32()