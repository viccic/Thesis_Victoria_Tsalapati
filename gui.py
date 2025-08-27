import customtkinter
from tkinterdnd2 import TkinterDnD
from Thinning import func_thinning
from tkinter import filedialog
import os

customtkinter.set_ctk_parent_class(TkinterDnD.Tk)
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("400x400")
app.title("Thinning")

# Global variables to store file paths
import_las_file = None
save_las_folder = None


# Slider callback
def slider_callback(value):
    my_slider_label.configure(text=int(value))


# Input file dialog
def openFile():
    global import_las_file
    filepath = filedialog.askopenfilename(filetypes=[("LAS files", "*.las")])
    if filepath:
        import_las_file = filepath
        # print(f"Selected file: {import_las_file}")


# Output folder dialog
def chooseSaveFolder():
    global save_las_folder
    folderpath = filedialog.askdirectory()
    if folderpath:
        save_las_folder = folderpath
        # print(f"Selected folder: {save_las_folder}")


# Run thinning and close app
def run_thinning():
    if not import_las_file or not save_las_folder:
        # print("Please select both input LAS file and output folder.")
        return

    percentage = int(my_slider.get())
    input_name = os.path.splitext(os.path.basename(import_las_file))[0]
    output_las_path = os.path.join(save_las_folder, f'{input_name}_thinned_{percentage}.las')

    func_thinning(import_las_file, percentage, output_las_path)
    app.destroy()


# Bind Enter to run_thinning
app.bind('<Return>', lambda event: run_thinning())

# Widgets
customtkinter.CTkLabel(app, text="Remaining Points After Thinning (%)", font=("Helvetica", 15)).pack(pady=(20, 0))

my_slider = customtkinter.CTkSlider(app, from_=0, to=100, command=slider_callback)
my_slider.pack(pady=10)
my_slider.set(50)

my_slider_label = customtkinter.CTkLabel(app, text="50", font=("Helvetica", 10))
my_slider_label.pack(pady=10)

import_button = customtkinter.CTkButton(
    app,
    text="Import LAS File",
    command=openFile,
    font=("Helvetica", 14),
    height=40,
    width=160
)
import_button.pack(pady=10)

save_button = customtkinter.CTkButton(
    app,
    text="Choose Output Folder",
    command=chooseSaveFolder,
    font=("Helvetica", 14),
    height=40,
    width=160
)
save_button.pack(pady=10)

run_button = customtkinter.CTkButton(
    app,
    text="Run Thinning",
    command=run_thinning,
    font=("Helvetica", 14),
    height=40,
    width=160
)
run_button.pack(pady=20)

app.mainloop()
