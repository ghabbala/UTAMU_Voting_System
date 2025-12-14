# utils.py
THEME_RED = "#b30000"
THEME_RED_ALT = "#ca0d1d"
THEME_WHITE = "white"

def center_window(window, width: int, height: int):
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
