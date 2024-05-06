import matplotlib.pyplot as plt
from PIL import Image
import os
import matplotlib.patches as patches

# Define the base path where your images are stored
base_path = (
    r"F:\CS 543\Project\BestResults"  # Update this with the actual path to your images
)
# Set up the plot
fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(16, 16))
fig.suptitle("Image Transformations", fontsize=20)  # Title for the entire plot

# List all image files
all_images = sorted(os.listdir(base_path))
# Filter out original images based on known original image names
originals = ["Camp1.jpg", "Camp2.jpg", "imageDay.png", "roadDay.png"]

for i, original in enumerate(originals):
    # Load the original image and resize
    img_path = os.path.join(base_path, original)
    img = Image.open(img_path).resize((256, 256))
    axes[i][0].imshow(img)
    axes[i][0].axis("off")
    axes[i][0].set_title("Original")

    # Find and load the modified images (assumes modifications start right after the original name)
    prefix = original.split(".")[0]  # Get the base name without file extension
    modified_images = [
        img for img in all_images if img.startswith(prefix) and img != original
    ]

    # Display up to 3 modified images
    for j, modified in enumerate(modified_images[:3]):
        img_path = os.path.join(base_path, modified)
        img = Image.open(img_path).resize((256, 256))
        axes[i][j + 1].imshow(img)
        axes[i][j + 1].axis("off")

        # Extract transformation label from filename
        transformation = (
            modified.replace(prefix, "").replace(".jpg", "").replace(".png", "")
        )
        transformation = transformation.replace("_", "").replace("result", "").strip()
        axes[i][j + 1].set_title(transformation)


# Adjust layout to prevent overlap
plt.tight_layout(
    rect=[0, 0.03, 1, 0.95]
)  # Adjust the rect to make room for the suptitle
plt.show()
