import tkinter as tk
from modules.constants import *
from PIL import Image, ImageTk


class AppMenuFrame(tk.Frame):
    """Main menu with app icons"""
    
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_COLOR)
        self.ctrl = ctrl
        self.btns = []
        self.lbls = []
    
    def _clear(self):
        """Destroy existing widgets"""
        for w in self.btns + self.lbls:
            w.destroy()
        self.btns = []
        self.lbls = []
    
    def _build(self):
        """Create app icons"""
        for i, app in enumerate(MENU_APPS):
            self._add_app(app['icon'], app['name'], app['frame'], i)
    
    def _add_app(self, icon_path, name, target, idx):
        """Create app button with label"""
        img = Image.open(icon_path).resize(MENU_ICON_SIZE, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        x = (idx % 3) * MENU_SPACING_X + MENU_START_X
        y = (idx // 3) * MENU_SPACING_Y + MENU_START_Y
        
        btn = tk.Label(self.ctrl, image=photo, bg=BG_COLOR,
                      cursor="hand2", highlightthickness=0, bd=0)
        btn.image = photo
        btn.place(x=x, y=y)
        btn.bind("<Button-1>", lambda e, t=target: self.ctrl.show(t))
        self.btns.append(btn)
        
        lbl = tk.Label(self.ctrl, text=name, font=TITLE_FONT, fg=TEXT_COLOR,
                      bg=BG_COLOR, highlightthickness=0, bd=0)
        lbl.place(x=x + MENU_LABEL_OFFSET_X, y=y + MENU_LABEL_OFFSET_Y, anchor="center")
        self.lbls.append(lbl)
    
    def on_show(self):
        """Called when frame is displayed"""
        self._clear()
        self._build()
        self.ctrl.set_bg(ROTOM_PHONE_BG)