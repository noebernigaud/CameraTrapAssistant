import tkinter as tk
from tkintermapview import TkinterMapView
from .config import load_map_state, save_map_state
import logging

def open_map_window(root, coord_var):
    """
    Opens a new window with a map. On click, closes and sets coordinates, saving them to ini.
    coord_var: tk.StringVar to update with the selected coordinates.
    """
    def on_map_click(coords):
        lat, lon = coords  # coords is a (lat, lon) tuple
        if hasattr(open_map_window, 'marker') and open_map_window.marker:
            open_map_window.marker.delete()
        open_map_window.marker = map_widget.set_marker(lat, lon)
        # Save and display coordinates
        coord_var.set(f"{lat:.5f}, {lon:.5f}")
        save_map_state(lat, lon, map_widget.zoom)
        logging.info(f"Saved coordinates: {lat:.5f}, {lon:.5f}")
        map_win.after(500, map_win.destroy)

    map_win = tk.Toplevel(root)
    map_win.title("Select coordinates")
    map_win.geometry("600x400")
    map_widget = TkinterMapView(map_win, width=600, height=400, corner_radius=0)
    map_widget.pack(fill="both", expand=True)
    lat, lon, zoom = load_map_state()
    map_widget.set_position(lat, lon)
    map_widget.set_zoom(zoom)
    open_map_window.marker = None
    map_widget.add_left_click_map_command(on_map_click)
    return map_win
