import tkinter as tk
from typing import Optional

class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget: tk.Widget = widget
        self.text: str = text
        self.tip_window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4, ipady=2)

    def hide_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class _BaseWithTooltip(tk.Frame):
    def __init__(self, parent: tk.Widget, text: str, tooltip_text: str, widget_type, widget_kwargs=None, **kwargs):
        frame_kwargs = dict(kwargs)
        if "width" not in frame_kwargs:
            frame_kwargs["width"] = 252
        if "height" not in frame_kwargs:
            frame_kwargs["height"] = 16
        super().__init__(parent, **frame_kwargs)
        self.pack_propagate(False)
        widget_kwargs = widget_kwargs or {}
        widget_type(self, text=text, anchor="w", **widget_kwargs).pack(side=tk.LEFT)
        info_icon = tk.Label(
            self,
            text="🛈",
            font=("Segoe UI", 11),
            fg="#747474",
            cursor="question_arrow"
        )
        info_icon.pack(side=tk.LEFT)
        ToolTip(info_icon, tooltip_text)

class CheckWithTooltip(_BaseWithTooltip):
    def __init__(self, parent: tk.Widget, text: str, variable: tk.BooleanVar, tooltip_text: str, **kwargs):
        widget_kwargs = {"variable": variable}
        super().__init__(parent, text, tooltip_text, tk.Checkbutton, widget_kwargs, **kwargs)

class LabelWithTooltip(_BaseWithTooltip):
    def __init__(self, parent: tk.Widget, text: str, tooltip_text: str, **kwargs):
        super().__init__(parent, text, tooltip_text, tk.Label, None, **kwargs)