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
import tkinter.messagebox as messagebox


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
            command=lambda: self.threaded_apply_model("fogg"),
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

        self.segmentation_button = tk.Button(
            self.ribbon_frame,
            text="Image Segmentation",
            bg="#03F4FD",
            fg="black",
            command=lambda: self.threaded_apply_model("im2seg"),
        )
        self.segmentation_button.pack(side="left", padx=5)

        self.view_recent_button = tk.Button(
            self.ribbon_frame,
            text="View Recent Generations",
            bg="#FFD700",
            fg="black",
            command=self.view_recent_generations,  # Adjust this to reference the correct method path
        )
        self.view_recent_button.pack(side="left", padx=5)

        self.original_image_label = tk.Label(self.left_panel, bg="#f5f5f5")
        self.original_image_label.pack(expand=True)

        self.duplicate_image_label = tk.Label(self.right_panel, bg="#f5f5f5")
        self.duplicate_image_label.pack(expand=True)
        self.model_threads = {}  # Dictionary to store threads
        self.model_type = None
        # Storing current image path for operations
        self.current_image_path = ""
        self.start_time = time.time()
        # Semaphore to limit the number of active threads
        self.thread_semaphore = threading.Semaphore(4)
        # Start the timer
        self.update_timer()
        print(f" print wk from tkinter app {os.getcwd()}")

    def view_recent_generations(self):
        # Hide the current page and all others might be visible
        self.master.switch_to_page(None)

        # Check if the 'recent_generations' page already exists in the pages dictionary
        if (
            "recent_generations" not in self.master.pages
            or self.master.pages["recent_generations"] is None
        ):
            # If the page doesn't exist, create it
            self.master.pages["recent_generations"] = DisplayGanifiedImages(
                self.master, self.master.go_back, ["./FoggyImg", "./CycleGanImg"]
            )

        # Switch to the 'recent_generations' page
        self.master.switch_to_page("recent_generations")

    # Message bOx

    def show_task_complete_popup(self, model_name):
        model_mapping = {
            "summer2winter": "Summer to Winter",
            "winter2summer": "Winter to Summer",
            "normal2snow": "Normal to Snow",
            "snow2normal": "Snow to Normal",
            "day2night": "Day to Night",
            "day2sunrise": "Day to Sunrise",
            "night2day": "Night to Day",
            "sunrise2day": "Sunrise to Day",
            "im2seg": "Image Segmentation",
        }

        message = (
            f"Task of applying {model_mapping[model_name]} has completed successfully"
        )

        messagebox.showinfo("Task Complete", message)

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

    def setup(self, image_path):
        # Add your existing setup code or image display logic here
        self.display_image(image_path)

    def apply_fog(self):
        if self.current_image_path:
            fogged_image_path = add_fog(self.current_image_path)
            image = Image.open(fogged_image_path)
            image = image.resize((600, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            # Complete the progress when done
            self.update_progress(100 - self.progress["value"])
            self.duplicate_image_label.config(image=photo)
            self.duplicate_image_label.image = photo

    def apply_model(self, model_type):
        if self.current_image_path:
            cyclegan(model_type, self.current_image_path)
            image_filename = (
                f"{Path(self.current_image_path).stem}_result_{model_type}.jpg"
            )
            output_image_path = f"./CycleGanImg/{image_filename}"
            # Wait until the file is created
            while not os.path.exists(output_image_path):
                time.sleep(0.1)  # Adjust the sleep interval as needed
            image = Image.open(output_image_path)
            image = image.resize((600, 600), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            # Complete the progress when done
            self.update_progress(100 - self.progress["value"])
            # Update the display with the new image
            self.duplicate_image_label.config(image=photo)
            self.duplicate_image_label.image = photo
            self.show_task_complete_popup(model_type)
            # Remove the thread from the dictionary once completed
            del self.model_threads[model_type]
            # Release the semaphore to allow another thread to start
            self.thread_semaphore.release()

    def threaded_apply_model(self, model_type):
        # Reset progress bar
        self.progress["value"] = 0
        self.update_progress(5)  # Initial quick update for better UX
        if model_type == "fogg":
            threading.Thread(target=self.apply_fog, daemon=True).start()
        else:
            # Acquire the semaphore before starting the thread
            if self.thread_semaphore.acquire(blocking=False):
                # Start the thread for applying the model
                thread = threading.Thread(
                    target=self.apply_model, args=(model_type,), daemon=True
                )
                self.model_threads[model_type] = (
                    thread  # Store the thread in the dictionary
                )
                thread.start()
            else:
                messagebox.showinfo("Info", "Maximum number of threads reached.")

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


class DisplayGanifiedImages(tk.Frame):
    def __init__(self, master, on_go_back, recent_folders):
        super().__init__(master, bg="lightgreen")
        self.master.title("View Recent Generations")
        self.recent_folders = recent_folders
        self.on_go_back = on_go_back
        self.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self, bg="lightgreen")
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="lightgreen")
        self.ribbon_frame = tk.Frame(self, bg="#e1e1e1", height=12)
        self.ribbon_frame.pack(side="bottom", fill="x", expand=False)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
        )
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.back_button = tk.Button(
            self.ribbon_frame,
            text="↩",
            bg="#0078D7",
            fg="white",
            command=on_go_back,
        )
        self.back_button.pack(side="bottom", fill="x", padx=10, pady=10)

        self.loaded_images = []
        self.bind("<Visibility>", lambda event: self.reload_images())

    def reload_images(self):
        self.clear_images()
        self.load_and_display_images()

    def clear_images(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.loaded_images.clear()

    def load_and_display_images(self):
        recent_images = self.find_recent_images()
        self.loaded_images.clear()
        for image_path in recent_images:
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image.resize((400, 400), Image.LANCZOS))
            self.add_image_to_display(photo, image_path)

    def find_recent_images(self):
        recent_images = []
        current_time = time.time()
        for folder in self.recent_folders:
            if os.path.exists(folder):
                while not os.path.exists(folder):
                    time.sleep(0.1)  # Adjust the sleep interval as needed
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        modified_time = os.path.getmtime(filepath)
                        if (
                            current_time - modified_time <= 600
                        ):  # Considered as recent if modified within last 10 minutes
                            recent_images.append(filepath)
        return recent_images

    def add_image_to_display(self, photo, image_path):
        if len(self.loaded_images) % 2 == 0:
            self.row_frame = tk.Frame(self.scrollable_frame, bg="lightgreen")
            self.row_frame.pack(fill="x", expand=True)
        self.loaded_images.append((photo, image_path))
        self.display_image(photo, self.row_frame, os.path.basename(image_path))

    def display_image(self, photo, parent_frame, filename):
        image_frame = tk.Frame(
            parent_frame,
            bg="#2EF3FF",
        )
        image_widget = tk.Label(image_frame, image=photo, bg="yellow")
        image_widget.image = photo  # Keep a reference to avoid garbage collection
        image_widget.pack(padx=10, pady=10)

        fname = filename.split("_")
        if len(fname) > 2:
            transformation_name = fname[2][:-4].upper()
        else:
            transformation_name = fname[1][:-4].upper()
        label = tk.Label(
            image_frame,
            text=transformation_name,
            fg="black",
            bg="#2EF3FF",
            font=("Helvetica", 12, "bold"),
        )
        label.pack()

        image_frame.pack(side="left", expand=True, padx=20, pady=10, anchor="n")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)


class MainApplication(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("2100x900")
        self.resizable(False, False)
        self.page_stack = []
        self.init_methods()
        self.init_pages()

    def init_methods(self):
        self.switch_to_display_page = self._switch_to_display_page
        self.go_back = self._go_back

    def init_pages(self):
        self.pages = {
            "selection": ImageSelectionPage(self, self.switch_to_display_page),
            "display": None,  # Will be created dynamically
            "recent_generations": None,  # Will be created dynamically
        }
        self.current_page = None
        self.switch_to_page("selection")

    def _switch_to_display_page(self, image_path):
        self.switch_to_page("display", image_path)

    def _go_back(self):
        if self.page_stack:
            self.current_page.pack_forget()
            self.current_page = self.page_stack.pop()
            self.current_page.pack(expand=True, fill="both")

    def switch_to_page(self, page_name, *args):
        if self.current_page:
            self.current_page.pack_forget()
            self.page_stack.append(self.current_page)

        # If None is passed, do not attempt to switch to a new page
        if page_name is None:
            self.current_page = None
            return

        if page_name not in self.pages or self.pages[page_name] is None:
            if page_name == "display":
                self.pages[page_name] = ImageDisplayPage(self, self.go_back)
            elif page_name == "recent_generations":
                self.pages[page_name] = DisplayGanifiedImages(
                    self, self.go_back, ["FoggyImg", "CycleGanImg"]
                )

        self.current_page = self.pages[page_name]
        if args:
            self.current_page.setup(*args)
        self.current_page.pack(expand=True, fill="both")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
