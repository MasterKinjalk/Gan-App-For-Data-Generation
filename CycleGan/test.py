from PIL import Image
from options.test_options import TestOptions
from data.base_dataset import get_transform
from models import create_model
from torchvision.transforms import ToPILImage
from util.util import tensor2im
from pathlib import Path

try:
    import wandb
except ImportError:
    print(
        'Warning: wandb package cannot be found. The option "--use_wandb" will result in error.'
    )


def load_single_image(image_path, opt):
    """Load and transform a single image."""
    image = Image.open(image_path).convert("RGB")
    transform = get_transform(opt)
    transformed_image = transform(image)  # Apply the transform
    return {
        "A": transformed_image.unsqueeze(0),  # Add batch dimension
        "A_paths": image_path,
    }


if __name__ == "__main__":
    opt = TestOptions().parse()  # get test options
    opt.num_threads = 0  # test code only supports num_threads = 0
    opt.batch_size = 1  # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling
    opt.no_flip = True  # no flip
    opt.display_id = -1  # no visdom display
    opt.isTrain = False  # set model to inference mode
    print("***********************")
    # User specifies the image path directly or through command line
    image_path = opt.dataroot
    print("***********************")

    # Create a model
    model = create_model(opt)
    model.setup(opt)  # regular setup

    # Initialize logger for wandb if needed
    if opt.use_wandb:
        wandb.init(project=opt.wandb_project_name, name=opt.name, config=opt)

    # Load and process the single image
    data = load_single_image(image_path, opt)
    print("***********************")
    model.set_input(data)  # unpack data from data loader
    print("***********************")
    model.test()  # run inference
    print("***********************")
    visuals = model.get_current_visuals()  # get image results
    print("***********************")

    # Save the result image
    to_pil = ToPILImage()
    print("***********************")
    for label, image_tensor in visuals.items():
        if label == "fake":
            # Convert the tensor to an image array
            image_numpy = tensor2im(image_tensor)

            # Create a PIL image from the numpy array
            pil_image = Image.fromarray(image_numpy)

            # Save the image file
            pil_image.save(
                f"../CycleGanImg/{Path(image_path).stem}_result_{opt.name}.jpg"
            )

    print("Processing complete. Saved transformed image.")
