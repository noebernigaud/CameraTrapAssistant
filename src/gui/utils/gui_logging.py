import logging

class TkinterLogHandler(logging.Handler):
    """
    Logging handler that writes log messages to a Tkinter Text widget in a thread-safe way.
    """
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record):
        msg = self.format(record)
        self.log_widget.after(0, self._append, msg)

    def _append(self, msg):
        self.log_widget.config(state='normal')
        self.log_widget.insert('end', msg + '\n')
        self.log_widget.see('end')
        self.log_widget.config(state='disabled')
