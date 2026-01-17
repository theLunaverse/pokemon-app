import tkinter as tk
from modules.constants import *
from PIL import Image, ImageTk


class WelcomeFrame(tk.Frame):
    """Welcome screen with start button"""

    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_COLOR)
        self.ctrl = ctrl
        self.btn = None
        self._build()

    def _build(self):
        """Create start button"""
        img = Image.open(START_BUTTON_IMG).resize(
            (START_BTN_WIDTH, START_BTN_HEIGHT), Image.LANCZOS
        )
        photo = ImageTk.PhotoImage(img)

        self.btn = tk.Label(
            self.ctrl,
            image=photo,
            bg=LABEL_BG_COLOR,
            cursor="hand2",
            highlightthickness=0,
            bd=0,
        )
        self.btn.image = photo
        self.btn.place(x=START_BTN_X, y=START_BTN_Y)
        self.btn.bind("<Button-1>", lambda e: self._start())

    def on_show(self):
        """Called when frame is displayed"""
        if self.btn:
            self.btn.place(x=START_BTN_X, y=START_BTN_Y)
        else:
            self._build()
        self.ctrl.set_bg(START_SCREEN_BG)

    def _start(self):
        """Handle start button click"""
        if self.btn:
            self.btn.place_forget()
        self.ctrl.show("AppMenuFrame")
