import customtkinter
from tkinterdnd2 import TkinterDnD
from Thinning import func_thinning
from tkinter import filedialog
import os

# ---- CTk setup ----
customtkinter.set_ctk_parent_class(TkinterDnD.Tk)
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("400x400")
app.title("Menu")

# ---- Globals ----
import_las_file = None
save_las_folder = None
current_window = None  # track single open child window


def close_current_window():
    global current_window
    if current_window is not None and current_window.winfo_exists():
        current_window.destroy()
    current_window = None


def open_other(title, message):
    """Open a simple placeholder window, closing any existing one."""
    global current_window
    close_current_window()
    current_window = customtkinter.CTkToplevel(app)
    current_window.title(title)
    current_window.geometry("320x200")
    customtkinter.CTkLabel(current_window, text=message).pack(pady=20)


def open_thinning():
    """Open the Thinning window with controls, closing any existing one."""
    global current_window, import_las_file, save_las_folder
    close_current_window()

    win = customtkinter.CTkToplevel(app)
    win.title("Thinning Case")
    win.geometry("380x360")
    current_window = win  # register

    # --- Callbacks defined inside so they can access 'win' widgets ---
    def slider_callback(value):
        my_slider_label.configure(text=str(int(float(value))))

    def open_file():
        nonlocal import_las_file
        path = filedialog.askopenfilename(filetypes=[("LAS files", "*.las")])
        if path:
            import_las_file = path
            import_label.configure(text=os.path.basename(path))

    def choose_save_folder():
        nonlocal save_las_folder
        path = filedialog.askdirectory()
        if path:
            save_las_folder = path
            save_label.configure(text=path)

    def run_thinning():
        if not import_las_file or not save_las_folder:
            # You could show a small warning label instead of printing
            return
        percentage = int(my_slider.get())
        input_name = os.path.splitext(os.path.basename(import_las_file))[0]
        output_las_path = os.path.join(save_las_folder, f"{input_name}_thinned_{percentage}.las")
        func_thinning(import_las_file, percentage, output_las_path)
        win.destroy()  # close child window after completion

    # Bind Enter to run
    win.bind("<Return>", lambda _e: run_thinning())

    # --- UI ---
    customtkinter.CTkLabel(
        win, text="Remaining Points After Thinning (%)", font=("Helvetica", 15)
    ).pack(pady=(20, 6))

    my_slider = customtkinter.CTkSlider(win, from_=0, to=100, command=slider_callback)
    my_slider.pack(pady=6)
    my_slider.set(50)

    my_slider_label = customtkinter.CTkLabel(win, text="50", font=("Helvetica", 11))
    my_slider_label.pack(pady=6)

    import_btn = customtkinter.CTkButton(win, text="Import LAS File", command=open_file,
                                         font=("Helvetica", 14), height=40, width=180)
    import_btn.pack(pady=6)
    import_label = customtkinter.CTkLabel(win, text="No file selected", font=("Helvetica", 10))
    import_label.pack(pady=(0, 6))

    save_btn = customtkinter.CTkButton(win, text="Choose Output Folder", command=choose_save_folder,
                                       font=("Helvetica", 14), height=40, width=180)
    save_btn.pack(pady=6)
    save_label = customtkinter.CTkLabel(win, text="No folder selected", font=("Helvetica", 10))
    save_label.pack(pady=(0, 6))

    run_btn = customtkinter.CTkButton(win, text="Run Thinning", command=run_thinning,
                                      font=("Helvetica", 14), height=44, width=180)
    run_btn.pack(pady=14)


# ---- Main menu buttons ----
Thinning_button = customtkinter.CTkButton(
    app, text="Thinning", font=("Helvetica", 14), height=40, width=160,
    command=open_thinning
)
Thinning_button.pack(pady=15)

Point_Cloud_button = customtkinter.CTkButton(
    app, text="Point Cloud Case", font=("Helvetica", 14), height=40, width=160,
    command=lambda: open_other("Point Cloud Case", "This is the Point Cloud window")
)
Point_Cloud_button.pack(pady=15)

Alpha_Shape_button = customtkinter.CTkButton(
    app, text="Alpha Shape Case", font=("Helvetica", 14), height=40, width=160,
    command=lambda: open_other("Alpha Shape Case", "This is the Alpha Shape window")
)
Alpha_Shape_button.pack(pady=15)

Voxel_Grid_button = customtkinter.CTkButton(
    app, text="Voxel Grid Case", font=("Helvetica", 14), height=40, width=160,
    command=lambda: open_other("Voxel Grid Case", "This is the Voxel Grid window")
)
Voxel_Grid_button.pack(pady=15)

Convex_Hull_button = customtkinter.CTkButton(
    app, text="Convex Hull Case", font=("Helvetica", 14), height=40, width=160,
    command=lambda: open_other("Convex Hull Case", "This is the Convex Hull window")
)
Convex_Hull_button.pack(pady=15)

Exit_button = customtkinter.CTkButton(
    app, text="Exit", font=("Helvetica", 14), height=40, width=160, command=app.destroy
)
Exit_button.pack(pady=15)

app.mainloop()
