import tensorflow as tf
import os
from lib.dataset import DatasetInitializer
from lib.models import ModelsBuilder
from lib.train import Trainer
from lib.plot import plot_clear2fog_intensity

datasetInit = DatasetInitializer(256, 256)
models_builder = ModelsBuilder()

use_transmission_map = False  # @param{type: "boolean"}
use_gauss_filter = False  # @param{type: "boolean"}
use_resize_conv = False  # @param{type: "boolean"}

generator_clear2fog = models_builder.build_generator(
    use_transmission_map=use_transmission_map,
    use_gauss_filter=use_gauss_filter,
    use_resize_conv=use_resize_conv,
)
generator_fog2clear = models_builder.build_generator(use_transmission_map=False)

use_intensity_for_fog_discriminator = False  # @param{type: "boolean"}
discriminator_fog = models_builder.build_discriminator(
    use_intensity=use_intensity_for_fog_discriminator
)
discriminator_clear = models_builder.build_discriminator(use_intensity=False)

weights_path = "Fogg\\weights"


trainer = Trainer(
    generator_clear2fog, generator_fog2clear, discriminator_fog, discriminator_clear
)


print("Current working directory:", os.getcwd())
trainer.configure_checkpoint(weights_path=weights_path, load_optimizers=False)


def add_fog(img_path, save_directory="FoggyImg"):
    # Ensure the FoggyImg directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Load the image
    image_clear = tf.io.decode_png(tf.io.read_file(img_path), channels=3)
    image_clear, _ = datasetInit.preprocess_image_test(image_clear, 0)

    # Generate foggy effect
    step = 0.35
    fig = plot_clear2fog_intensity(generator_clear2fog, image_clear, step)

    # Define the filename for the foggy image based on the original image name
    base_filename = os.path.basename(
        img_path
    )  # Extract base name of the original image
    name_part = os.path.splitext(base_filename)[0]  # Remove the file extension
    foggy_filename = f"{name_part}_fogg.jpg"  # Append '_fogg' to the name
    save_path = os.path.join(save_directory, foggy_filename)  # Combine into a full path

    # Save the figure to the specified path
    fig.savefig(save_path, bbox_inches="tight", pad_inches=0)

    # Optionally, print the path for debugging
    print(f"Saved foggy image at: {save_path}")

    return save_path
