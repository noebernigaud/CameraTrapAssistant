
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import logging

# Import project utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from objects.options_config import OptionsConfig
from actions.run import runWithArgs
from GUI_utils.gui_logging import TkinterLogHandler
from GUI_utils.gui_config import load_checkbox_state, save_checkbox_state



def run_in_thread(folder, options_config, lat, lon):
    """
    Run the main processing in a background thread.
    """
    try:
        runWithArgs(folder, options_config, lat, lon)
        messagebox.showinfo("Success", "Execution successful.")
    except Exception as e:
        messagebox.showerror("Error", f"Execution failure : {e}")


def select_folder():
    """
    Handler for folder selection. Launches processing in a thread and saves checkbox state.
    """
    global folder
    folder = filedialog.askdirectory()
    if folder:
        label.config(text=f"{folder}")
        run_btn.config(state=tk.NORMAL)

def run():
    run_btn.config(state=tk.DISABLED)
    log_text.config(state='normal')
    log_text.delete(1.0, tk.END)
    log_text.config(state='disabled')
    options_config = OptionsConfig(
        generate_data = data_var.get(),
        generate_stats = stats_var.get(),
        move_empty = move_empty_var.get(),
        move_undefined = move_undefined_var.get(),
        rename_files = rename_var.get(),
        add_gps = gps_var.get(),
        prediction_threshold = threshold_var.get(),
        get_gps_from_each_file = get_gps_each_var.get(),
        use_gps_only_for_data = use_gps_only_for_data_var.get()
    )
    save_checkbox_state(options_config)
    lat, lon = None, None
    logging.info(f"run on folder {folder}")
    if options_config.add_gps:
        # Open map window automatically to select coordinates and wait for user
        from GUI_utils.gui_map import open_map_window, load_map_state
        # Create a modal Toplevel window for the map
        map_window = open_map_window(root, coord_var)
        if map_window is not None:
            map_window.grab_set()
            root.wait_window(map_window)
        lat, lon, _ = load_map_state()
        if lat is None or lon is None:
            messagebox.showerror("Error", "Please select coordinates on the map before adding GPS data.")
            return
        # Only start thread after coordinates are set
        threading.Thread(target=run_in_thread, args=(folder, options_config, lat, lon), daemon=True).start()
    else:
        threading.Thread(target=run_in_thread, args=(folder, options_config, lat, lon), daemon=True).start()


def main():
    """
    Main entry point for the DeepFaune GUI.
    Sets up the window, widgets, and logging.
    """
    global root, folder, label, log_text
    global data_var, stats_var, move_empty_var, move_undefined_var, rename_var, get_gps_each_var, use_gps_only_for_data_var, threshold_var
    global gps_var, coord_var
    root = tk.Tk()
    root.title("DeepFaune custom script")
    root.minsize(240, 120)

    # Folder selection and launch row
    folder_frame = tk.Frame(root)
    try:
        from pathlib import Path
        folder_icon = tk.PhotoImage(file=str(Path(__file__).parent.parent / "icons" / "folder.png"))
        run_icon = tk.PhotoImage(file=str(Path(__file__).parent.parent / "icons" / "run.png"))
        folder_icon = folder_icon.subsample(max(folder_icon.width() // 20, 1), max(folder_icon.height() // 20, 1))
        run_icon = run_icon.subsample(max(run_icon.width() // 20, 1), max(run_icon.height() // 20, 1))
    except Exception:
        folder_icon = None
        run_icon = None
    # Use grid for better expansion and height control
    folder_frame.columnconfigure(0, weight=1)
    label = tk.Label(
        folder_frame,
        text="No folder chosen...",
        font=("Arial", 10, "italic"),
        bg="white",
        bd=1,
        relief=tk.SUNKEN,
        anchor="e"
    )
    folder_btn = tk.Button(folder_frame, text=" Choose Folder ", image=folder_icon, compound=tk.LEFT, font=("Arial", 10, "bold"), command=select_folder)
    global run_btn
    run_btn = tk.Button(folder_frame, text="   Run   ", image=run_icon, compound=tk.LEFT, font=("Arial", 10, "bold"), command=run, state=tk.DISABLED)
    label.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=2, ipadx=10, ipady=0)
    folder_btn.grid(row=0, column=1, padx=(3, 5), pady=2, ipadx=8, ipady=4, sticky="e")
    run_btn.grid(row=0, column=2, padx=5, pady=2, ipadx=8, ipady=4, sticky="e")
    folder_frame.pack(pady=12, padx=10, fill="x", anchor="ne")
    folder_frame.folder_icon = folder_icon
    folder_frame.run_icon = run_icon

    # Options category title and separator
    options_title = tk.Label(root, text="Options", font=("Arial", 10, "bold"), anchor="w")
    options_title.pack(fill="x", padx=12, pady=(0, 0))
    options_separator = tk.Frame(root, height=1, bg="#cccccc", bd=0, relief=tk.FLAT)
    options_separator.pack(fill="x", padx=12, pady=(0, 8))

    # Load saved checkbox state
    options_config = load_checkbox_state()

    # --- Redesigned Options Section ---
    # Variables
    data_var = tk.BooleanVar(value=options_config.generate_data)
    stats_var = tk.BooleanVar(value=options_config.generate_stats)
    move_empty_var = tk.BooleanVar(value=options_config.move_empty)
    move_undefined_var = tk.BooleanVar(value=options_config.move_undefined)
    rename_var = tk.BooleanVar(value=options_config.rename_files)
    gps_var = tk.BooleanVar(value=options_config.add_gps)
    get_gps_each_var = tk.BooleanVar(value=options_config.get_gps_from_each_file)
    use_gps_only_for_data_var = tk.BooleanVar(value=options_config.use_gps_only_for_data)
    threshold_var = tk.DoubleVar(value=options_config.prediction_threshold)

    # Main options frame
    options_frame = tk.Frame(root)
    options_frame.pack(pady=5, fill="x")

    # Folder sort row
    folder_sort_frame = tk.Frame(options_frame)
    tk.Label(folder_sort_frame, text="Folder sort :", width=32, anchor="w").pack(side=tk.LEFT)
    tk.Checkbutton(folder_sort_frame, text="Empty results to subfolder", width=32, anchor="w", variable=move_empty_var).pack(side=tk.LEFT)
    tk.Checkbutton(folder_sort_frame, text="Undefined results to subfolder", width=32, anchor="w", variable=move_undefined_var).pack(side=tk.LEFT)
    folder_sort_frame.pack(fill="x", pady=1, padx=30)

    # Files update row
    files_update_frame = tk.Frame(options_frame)
    tk.Label(files_update_frame, text="Files update :", width=32, anchor="w").pack(side=tk.LEFT)
    tk.Checkbutton(files_update_frame, text="Rename with date and info", width=32, anchor="w", variable=rename_var).pack(side=tk.LEFT)
    tk.Checkbutton(files_update_frame, text="Add GPS location", width=32, anchor="w", variable=gps_var).pack(side=tk.LEFT)
    files_update_frame.pack(fill="x", pady=1, padx=30)

    # Data generation row
    data_gen_frame = tk.Frame(options_frame)
    tk.Label(data_gen_frame, text="Data generation :", width=32, anchor="w").pack(side=tk.LEFT)
    tk.Checkbutton(data_gen_frame, text="CSV file", width=32, anchor="w", variable=data_var).pack(side=tk.LEFT)
    tk.Checkbutton(data_gen_frame, text="Statistics files", width=32, anchor="w", variable=stats_var).pack(side=tk.LEFT)
    data_gen_frame.pack(fill="x", pady=1, padx=30)

    # --- More (foldable) section ---
    def toggle_more():
        if more_content.winfo_ismapped():
            more_content.pack_forget()
            more_btn.config(text="more ▼")
        else:
            more_content.pack(fill="x", pady=(2, 0))
            more_btn.config(text="more ▲")

    more_btn = tk.Button(options_frame, text="more ▼", font=("Arial", 10, "italic"), bd=0, fg="#444", cursor="hand2", command=toggle_more)
    more_btn.pack(anchor="w", pady=(6, 0), padx=20)

    more_content = tk.Frame(options_frame)
    # Prediction threshold slider
    threshold_row = tk.Frame(more_content)
    tk.Label(threshold_row, text="Adjust prediction threshold :", width=26, anchor="w").pack(side=tk.LEFT)
    threshold_slider = tk.Scale(threshold_row, from_=0.0, to=1.0, orient=tk.HORIZONTAL, resolution=0.01, variable=threshold_var, showvalue=True, length=180)
    threshold_slider.pack(side=tk.LEFT, padx=5)
    threshold_row.pack(fill="x", pady=2, padx=30)
    # More checkboxes
    tk.Checkbutton(more_content, text="Get GPS data for each video independently", variable=get_gps_each_var).pack(anchor="w", padx=30)
    tk.Checkbutton(more_content, text="Use added GPS data without updating files", variable=use_gps_only_for_data_var).pack(anchor="w", padx=30)
    # Start folded
    more_content.pack_forget()

    # Map selection variable (no button/field, but still needed for map window)
    coord_var = tk.StringVar(value="No coordinates selected")

    # Logs category title and separator
    logs_title = tk.Label(root, text="Logs", font=("Arial", 10, "bold"), anchor="w")
    logs_title.pack(fill="x", padx=12, pady=(0, 0))
    logs_separator = tk.Frame(root, height=1, bg="#cccccc", bd=0, relief=tk.FLAT)
    logs_separator.pack(fill="x", padx=12, pady=(0, 8))

    # Log text area
    log_text = tk.Text(root, height=10, width=60, state='disabled')
    log_text.pack(padx=10, pady=(0, 10), fill='both', expand=True)

    # Attach the logging handler
    handler = TkinterLogHandler(log_text)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    root.mainloop()


if __name__ == "__main__":
    main()
