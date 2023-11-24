from contextlib import contextmanager
import os
import glob
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from threading import Thread
from threading import Lock


supported_formats = [".JPG", ".jpg", ".png", ".PNG", ".jpeg", ".JPEG"]
DOWNSCALE_RATIO = 4
RESIZE_LOCK = Lock()
num_files = 0


window = tk.Tk()
window.title("Image Resizer")

label_read = tk.Label(window, text="Read from", font=40)
label_read.grid(row=0, column=0, padx=10, pady=10)
label_write = tk.Label(window, text="Write to", font=40)
label_write.grid(row=2, column=0, padx=10, pady=10)

input_read = tk.Entry(window, font=40, width=50)
input_read.grid(row=0, column=2, columnspan=6, padx=10, pady=10)
input_write = tk.Entry(window, font=40, width=50)
input_write.grid(row=2, column=2, columnspan=6, padx=10, pady=10)


def browsefunc(insert_to: tk.Entry):
    def x():
        # home = os.path.expanduser('~')
        # dir_path = filedialog.askdirectory(initialdir=home)
        dir_path = filedialog.askdirectory()
        insert_to.delete(0, tk.END)
        insert_to.insert(tk.END, dir_path)
    return x


button_read = tk.Button(window, text="open", font=40, command=browsefunc(input_read))
button_read.grid(row=0, column=8, padx=10, pady=10)

button_write = tk.Button(window, text="open", font=40, command=browsefunc(input_write))
button_write.grid(row=2, column=8, padx=10, pady=10)

text = tk.Text(window, height=10, width=50, state=tk.DISABLED)
text.grid(row=6, column=0, columnspan=6, padx=10, pady=10)


def add_text(textbox: tk.Text, msg):
    textbox.configure(state=tk.NORMAL)
    textbox.insert(tk.END, msg)
    textbox.configure(state=tk.DISABLED)
    textbox.see(tk.END)



def apply_resize():
    # Read the input folder path from input_read and read the output folder path
    # Traverse the input folder and resize all the images and save them in the output folder
    # Show the output in the text box
    read_folder_path = input_read.get()
    write_folder_path = input_write.get()
    read_folder = Path(read_folder_path)
    write_folder = Path(write_folder_path)
    
    if not read_folder_path:
        add_text(text, "Read folder path is empty\n")
        return
    
    if not write_folder_path:
        add_text(text, "Write folder path is empty\n")
        return
    
    if read_folder == write_folder:
        add_text(text, "Read and write folders cannot be the same\n")
        return
        
    if not read_folder.exists():
        add_text(text, f"Read folder {read_folder} does not exist\n")
        return
    
    if not write_folder.exists():
        add_text(text, f"Write folder {write_folder} does not exist\n")
        return
    
    global num_files
    num_files = 0

    add_text(text, f"Start resizing images in {read_folder}\n")
    add_text(text, f"Saving images in {write_folder}\n")

    def resize_images_in_folder(d: Path):
        for f in d.iterdir():
            if f.is_dir():
                resize_images_in_folder(f)
            if f.suffix in supported_formats:
                output_file = write_folder / f.relative_to(read_folder)
                if not output_file.parent.exists():
                    output_file.parent.mkdir(parents=True)
                image = Image.open(f)
                w, h = image.size
                image = image.resize((w // DOWNSCALE_RATIO, h // DOWNSCALE_RATIO))
                image.save(output_file)
                add_text(text, f"Saved {output_file}\n")
                global num_files
                num_files += 1

    resize_images_in_folder(read_folder)
    add_text(text, f"Done resizing {num_files} images\n")


def apply_resize_with_lock():
    print("Start")
    locked = RESIZE_LOCK.acquire(blocking=False)
    print(f"Get lock {locked}")
    try:
        if locked:
            apply_resize()
    finally:
        if locked:
            RESIZE_LOCK.release()
    print("End thread")


def apply_resize_thread(event=None):
    t = Thread(target=apply_resize_with_lock)
    t.start()


button_go = tk.Button(window, text="Go", font=40, command=apply_resize_thread)
button_go.grid(row=4, column=8, padx=10, pady=10)
window.bind('<Return>', apply_resize_thread)

# Add description of the tool
desc = tk.Text(window, height=10, width=50, state=tk.DISABLED)
desc.grid(row=8, column=0, columnspan=6, padx=10, pady=10)
add_text(
    desc,
    "This tool resizes all the images in the input folder and save them in the output folder\n."
    "The output folder structure is the same as the input folder structure\n"
    "The resized images are 1/4 of the original size\n"
    "Supported image formats are: " + ", ".join(supported_formats)
)

window.mainloop()
