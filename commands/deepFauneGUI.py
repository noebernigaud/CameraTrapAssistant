
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import logging

# Import project utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from actions.run import runWithArgs
from GUI_utils.gui_logging import TkinterLogHandler
from GUI_utils.gui_config import load_checkbox_state, save_checkbox_state



def run_in_thread(folder, do_data, do_move_empty, do_move_undefined, do_rename, do_gps, lat, lon):
    """
    Run the main processing in a background thread.
    """
    try:
        runWithArgs(folder, do_data, do_move_empty, do_move_undefined, do_rename, do_gps, lat, lon)
        messagebox.showinfo("Success", "Execution successful.")
    except Exception as e:
        messagebox.showerror("Error", f"Execution failure : {e}")



def select_folder():
    """
    Handler for folder selection. Launches processing in a thread and saves checkbox state.
    """
    folder = filedialog.askdirectory()
    if folder:
        label.config(text=f"Chosen folder : {folder}")
        log_text.config(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.config(state='disabled')
        do_data = data_var.get()
        do_move_empty = move_empty_var.get()
        do_move_undefined = move_undefined_var.get()
        do_rename = rename_var.get()
        do_gps = gps_var.get()
        save_checkbox_state(do_data, do_move_empty, do_move_undefined, do_rename, do_gps)
        lat, lon = None, None
        if do_gps:
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
            threading.Thread(target=run_in_thread, args=(folder, do_data, do_move_empty, do_move_undefined, do_rename, do_gps, lat, lon), daemon=True).start()
        else:
            threading.Thread(target=run_in_thread, args=(folder, do_data, do_move_empty, do_move_undefined, do_rename, do_gps, lat, lon), daemon=True).start()


def main():
    """
    Main entry point for the DeepFaune GUI.
    Sets up the window, widgets, and logging.
    """
    global root, label, log_text, data_var, move_empty_var, move_undefined_var, rename_var, gps_var, coord_var
    root = tk.Tk()
    root.title("DeepFaune custom script")
    root.minsize(240, 120)

    # Folder selection
    folder_frame = tk.Frame(root)
    label = tk.Label(folder_frame, text="No folder chosen")
    btn = tk.Button(folder_frame, text="Choose a folder", command=select_folder)
    label.pack(side=tk.LEFT, padx=5)
    btn.pack(side=tk.LEFT, padx = 5)
    folder_frame.pack(pady=5)

    # Load saved checkbox state
    do_data_default, do_move_empty_default, do_move_undefined_default, do_rename_default, do_gps_default = load_checkbox_state()

    # Checkboxes
    options_frame = tk.Frame(root)
    data_var = tk.BooleanVar(value=do_data_default)
    move_empty_var = tk.BooleanVar(value=do_move_empty_default)
    move_undefined_var = tk.BooleanVar(value=do_move_undefined_default)  # Default to False for undefined
    rename_var = tk.BooleanVar(value=do_rename_default)  # Default to False for renaming
    gps_var = tk.BooleanVar(value=do_gps_default)
    data_cb = tk.Checkbutton(options_frame, text="Generate data (CSV)", variable=data_var)
    move_empty_cb = tk.Checkbutton(options_frame, text="Move empty videos to subfolder", variable=move_empty_var)
    move_undefined_cb = tk.Checkbutton(options_frame, text="Move non-identified videos to subfolder", variable=move_undefined_var)
    rename_cb = tk.Checkbutton(options_frame, text="Rename files with date and info", variable=rename_var)
    gps_cb = tk.Checkbutton(options_frame, text="Add GPS data to vidéos", variable=gps_var)
    data_cb.pack(side=tk.LEFT, padx=5)
    move_empty_cb.pack(side=tk.LEFT, padx=5)
    move_undefined_cb.pack(side=tk.LEFT, padx=5)
    rename_cb.pack(side=tk.LEFT, padx=5)
    gps_cb.pack(side=tk.LEFT, padx=5)
    options_frame.pack(pady=5)

    # Map selection variable (no button/field, but still needed for map window)
    coord_var = tk.StringVar(value="No coordinates selected")

    # Log text area
    log_text = tk.Text(root, height=10, width=60, state='disabled')
    log_text.pack(padx=10, pady=10, fill='both', expand=True)

    # Attach the logging handler
    handler = TkinterLogHandler(log_text)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    root.mainloop()


if __name__ == "__main__":
    main()
