import sys
import gc
import os
from contextlib import contextmanager
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import ttk
from pathlib import Path
import time
import threading


@contextmanager
def model_context(path):
    # Manage sys.path
    original_path = sys.path.copy()
    sys.path.append(path)
    try:
        yield
    finally:
        # Restore the original path
        sys.path = original_path
        # Clear any system-specific or Python-specific garbage
        gc.collect()


with model_context("./Fogg"):
    from Fogg.foggy_function import add_fog

with model_context("./CycleGan"):
    from cyclegan_function import cyclegan


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


ensure_directory("CycleGanImg")  # Ensure the CycleGanImg directory exists
ensure_directory("FoggyImg")


class ImageSelectionPage(tk.Frame):
    """Image selection page with drag and drop and button functionality."""

    def __init__(self, master, on_image_selected):
        super().__init__(master, bg="#f0f0f0")  # Light grey background

        self.on_image_selected = on_image_selected
        self.master.title("Select Image")
        self.pack(fill="both", expand=True)

        # Enable drag and drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

        # Instruction label with click event
        self.label = tk.Label(
            self,
            text="Drag and drop an image here or click to select",
            font=("Helvetica", 14),
            bg="#f0f0f0",
            pady=1,
        )
        self.label.pack(anchor="n")
        self.label.bind("<Button-1>", self.on_click)

        # Plus button with styling
        self.plus_button = tk.Button(
            self,
            text="+",
            font=("Roboto", 30),
            width=3,
            height=1,
            command=self.on_click,
            relief=tk.RAISED,
            bg="#0078D7",
            fg="white",
        )
        self.plus_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Status bar
        self.status = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.label.bind("<Button-1>", self.on_click)

    def on_drop(self, event):
        file_path = (
            event.data.strip().replace("{", "").replace("}", "")
        )  # Removing potential curly braces
        if file_path:
            self.on_image_selected(file_path)

    def on_click(self, event=None):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if file_path:
            self.on_image_selected(file_path)


class ImageDisplayPage(tk.Frame):
    def __init__(self, master, on_go_back):
        super().__init__(master, bg="#f5f5f5")  # Setting a light grey background color
        self.master.title("View and Generated Image")
        self.on_go_back = on_go_back
        self.pack(fill="both", expand=True)

        # Left and right panels for original and duplicate images
        self.left_panel = tk.Frame(self, bg="lightblue")
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        # Boundary line between panels
        self.separator = tk.Frame(self, width=2, bg="black", padx=2)
        self.separator.grid(row=0, column=1, sticky="ns")

        self.right_panel = tk.Frame(self, bg="lightgreen")
        self.right_panel.grid(row=0, column=2, sticky="nsew")

        self.bottom_frame = tk.Frame(self, bg="lightyellow")
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Ribbon frame for navigation or additional controls
        self.ribbon_frame = tk.Frame(self, bg="#e1e1e1")
        self.ribbon_frame.grid(row=2, column=0, columnspan=3, sticky="ew")

        # Configure grid layout to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # For separator, minimal expansion
        self.grid_columnconfigure(2, weight=1)

        # Progress bar and timer in right panel
        self.progress = ttk.Progressbar(
            self.right_panel, orient="horizontal", mode="determinate", length=100
        )
        self.progress.pack(pady=20, padx=20)
        # Timer label with StringVar
        self.time_var = tk.StringVar()
        self.time_var.set("Time: 0s")
        self.timer_label = tk.Label(
            self.ribbon_frame, textvariable=self.time_var, bg="lightgreen"
        )
        self.timer_label.pack(side="right", pady=5)

        # # Buttons for weather and city
        # button_frame = tk.Frame(self.left_panel, bg='#f5f5f5')
        # button_frame.pack(pady=10)

        self.back_button = tk.Button(
            self.ribbon_frame,
            text="↩",
            bg="#0078D7",
            fg="white",
            command=self.on_go_back,
        )
        self.back_button.pack(side="left", padx=10, pady=10)

        self.summer_button = tk.Button(
            self.ribbon_frame,
            text="Summer",
            bg="#ffcc00",
            fg="black",
            command=lambda: self.threaded_apply_model(
                "summer2winter"
            ),  # Adjusted model type if needed
        )
        self.summer_button.pack(side="left", padx=5)

        self.snow_button = tk.Button(
            self.ribbon_frame,
            text="Snow",
            bg="#0078D7",
            fg="white",
            command=lambda: self.threaded_apply_model("normal2snow"),
        )
        self.snow_button.pack(side="left", padx=5)

        self.winter_button = tk.Button(
            self.ribbon_frame,
            text="Winter",
            bg="#4CAF50",
            fg="white",
            command=lambda: self.threaded_apply_model(
                "winter2summer"
            ),  # Adjusted model type if needed
        )
        self.winter_button.pack(side="left", padx=5)

        self.foggy_button = tk.Button(
            self.ribbon_frame,
            text="Foggy",
            bg="#888888",
            fg="white",
            command=self.apply_fog,
        )
        self.foggy_button.pack(side="left", padx=5)

        self.day_button = tk.Button(
            self.ribbon_frame,
            text="Day",
            bg="#4B0082",
            fg="white",
            command=lambda: self.threaded_apply_model("night2day"),
        )
        self.day_button.pack(side="left", padx=5)

        self.night_button = tk.Button(
            self.ribbon_frame,
            text="Night",
            bg="#000080",
            fg="white",
            command=lambda: self.threaded_apply_model("day2night"),
        )
        self.night_button.pack(side="left", padx=5)

        self.sunrise_button = tk.Button(
            self.ribbon_frame,
            text="Day To Sunrise",
            bg="#FFD700",
            fg="black",
            command=lambda: self.threaded_apply_model("day2sunrise"),
        )
        self.sunrise_button.pack(side="left", padx=5)

        self.sunrise2day_button = tk.Button(
            self.ribbon_frame,
            text="Sunrise To Day",
            bg="#FADADD",
            fg="black",
            command=lambda: self.threaded_apply_model("sunrise2day"),
        )
        self.sunrise2day_button.pack(side="left", padx=5)

        self.original_image_label = tk.Label(self.left_panel, bg="#f5f5f5")
        self.original_image_label.pack(expand=True)

        self.duplicate_image_label = tk.Label(self.right_panel, bg="#f5f5f5")
        self.duplicate_image_label.pack(expand=True)

        # Storing current image path for operations
        self.current_image_path = ""
        self.start_time = time.time()

        # Start the timer
        self.update_timer()

    def display_image(self, image_path):
        self.current_image_path = image_path  # Store the current path
        image = Image.open(image_path)
        image = image.resize((600, 600), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # Display original and duplicate images
        self.original_image_label.config(image=photo)
        self.original_image_label.image = photo  # Keep a reference
        self.duplicate_image_label.config(image=photo)
        self.duplicate_image_label.image = photo  # Keep a reference

    def apply_fog(self):
        if self.current_image_path:
            fogged_image_path = add_fog(self.current_image_path)
            image = Image.open(fogged_image_path)
            image = image.resize((600, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            self.duplicate_image_label.config(image=photo)
            self.duplicate_image_label.image = photo

    def apply_model(self, model_type):
        if self.current_image_path:
            cyclegan(model_type, self.current_image_path)
            time.sleep(2)  # Simulating a long-running task
            self.update_progress(5)
            image = Image.open(
                f"./CycleGanImg/{Path(self.current_image_path).stem}_result_{model_type}.jpg"
            )
            image = image.resize((600, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            # Complete the progress when done
            self.update_progress(100 - self.progress["value"])
            # Update the display with the new image
            self.duplicate_image_label.config(image=photo)
            self.duplicate_image_label.image = photo

    def threaded_apply_model(self, model_type):
        # Reset progress bar
        self.progress["value"] = 0
        self.update_progress(5)  # Initial quick update for better UX

        # Start the long-running task in a new thread
        threading.Thread(
            target=self.apply_model, args=(model_type,), daemon=True
        ).start()

    def update_progress(self, increment):
        # Incrementally update the progress bar
        self.progress["value"] += increment
        self.update_idletasks()  # Update the UI thread
        if self.progress["value"] >= 100:
            self.progress["value"] = 100  # Cap the progress bar
        else:
            # Schedule another update
            self.after(1000, lambda: self.update_progress(increment))

    def update_timer(self):
        # Update the timer every second
        elapsed_time = int(time.time() - self.start_time)
        self.time_var.set(f"Time: {elapsed_time}s")
        self.after(1000, self.update_timer)  # Schedule next update after 1 second


class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("2100x900")

        self.selection_page = ImageSelectionPage(self, self.switch_to_display_page)
        self.display_page = None

    def switch_to_display_page(self, image_path):
        if self.display_page:
            self.display_page.destroy()

        self.display_page = ImageDisplayPage(self, self.go_back)
        self.display_page.display_image(image_path)
        self.selection_page.pack_forget()
        self.display_page.pack()

    def go_back(self):
        if self.display_page:
            self.display_page.pack_forget()

        self.selection_page.pack()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
