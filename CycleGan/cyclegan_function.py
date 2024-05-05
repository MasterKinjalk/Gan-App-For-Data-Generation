import subprocess
import os


def cyclegan(model, img_path):
    # Map model names to their respective pre-trained versions
    model_mapping = {
        "summer2winter": "summer2winter",
        "winter2summer": "winter2summer",
        "normal2snow": "normal2snow",
        "snow2normal": "snow2normal",
        "day2night": "day2night",
        "day2sunrise": "day2sunrise",
        "night2day": "night2day",
        "sunrise2day": "sunrise2day",
        "im2seg": "im2seg",
    }
    if model not in model_mapping:
        raise ValueError("Model not recognized or supported.")

    cur_path = os.getcwd()
    os.chdir("F:/CS 543/Project/CycleGan")

    model_name = model_mapping[model]
    python_executable = "F:/CS 543/Project/venv/Scripts/python.exe"  # Path to Python executable in your virtual environment
    test_script = "F:/CS 543/Project/CycleGan/test.py"
    if model_name == "im2seg":
        command = [
            python_executable,  # Use Python executable from virtual environment
            test_script,
            "--dataroot",
            img_path,
            "--name",
            model_name,
            "--model",
            "test",
            "--netG",
            "unet_256",
            "--direction",
            "BtoA",
            "--dataset_mode",
            "single",
            "--norm",
            "batch",
        ]
    else:
        command = [
            python_executable,  # Use Python executable from virtual environment
            test_script,
            "--dataroot",
            img_path,
            "--name",
            model_name,
            "--model",
            "test",
            "--no_dropout",
            "--num_test",
            "1",
            "--preprocess",
            "resize_and_crop",
        ]
    # Change to the CycleGan directory
    try:
        # Execute the command
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print("CycleGAN processing completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error during CycleGAN processing:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise
    finally:
        os.chdir(cur_path)


# if __name__ == "__main__":
#     cyclegan(
#         "im2seg",
#         "F:/CS 543/Project/bgscene.png",
#     )
#     print("&&&&&&&&&&&&&&&&&&&&")
