from PIL import Image
from options.test_options import TestOptions
from data.base_dataset import get_transform
from models import create_model
from torchvision.transforms import ToPILImage
from util.util import tensor2im
from pathlib import Path

import wandb

def load_single_image(image_path, opt):
    image = Image.open(image_path).convert("RGB")
    transform = get_transform(opt)
    transformed_image = transform(image)
    return {
        "A": transformed_image.unsqueeze(0),
        "A_paths": image_path,
    }


if __name__ == "__main__":
    opt = TestOptions().parse()
    opt.num_threads = 0 
    opt.batch_size = 1
    opt.serial_batches = True 
    opt.no_flip = True 
    opt.display_id = -1
    opt.isTrain = False 
    image_path = opt.dataroot

    model = create_model(opt)
    model.setup(opt)

    if opt.use_wandb:
        wandb.init(project=opt.wandb_project_name, name=opt.name, config=opt)

    data = load_single_image(image_path, opt)

    model.set_input(data) 

    model.test() 

    visuals = model.get_current_visuals()

    to_pil = ToPILImage()

    for label, image_tensor in visuals.items():
        if label == "fake":
            image_numpy = tensor2im(image_tensor)
            pil_image = Image.fromarray(image_numpy)
            pil_image.save(
                f"../CycleGanImg/{Path(image_path).stem}_result_{opt.name}.jpg"
            )

    print("Processing complete. Saved transformed image.")
