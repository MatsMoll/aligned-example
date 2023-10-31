from aligned import feature_view, Int32
from aligned.compiler.feature_factory import ImageUrl
from examples.mnist.source import mnist_source

@feature_view(
    "mnist",
    batch_source= mnist_source,
    description="Features desrcribing the mnist features",
)
class MnistFeature:

    id = Int32().as_entity()
    image_url = ImageUrl()

    image = image_url.load_image()
    grayscale_image = image.to_grayscale()

    label = Int32()