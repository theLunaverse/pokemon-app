import tkinter as tk
from PIL import Image, ImageTk
from modules.constants import *


class ErrorHandler:
    """Handles error popups across the app"""
    
    _img_cache = {}
    
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.popup = None
    
    def show(self, msg, retry_cb=None):
        """Show error popup with optional retry"""
        self.close()
        
        self.popup = tk.Frame(self.ctrl, bg=CARD_BG_COLOR, width=ERROR_POPUP_WIDTH, 
                             height=ERROR_POPUP_HEIGHT, highlightbackground=ACCENT_COLOR, 
                             highlightthickness=3)
        self.popup.place(x=ERROR_POPUP_X, y=ERROR_POPUP_Y)
        self.popup.pack_propagate(False)
        
        # Content
        cont = tk.Frame(self.popup, bg=CARD_BG_COLOR)
        cont.place(relx=0.5, rely=0.45, anchor="center")
        
        # Error image
        err_img = self._load_img(ERROR_IMG, ERROR_IMG_SIZE)
        if err_img:
            img_lbl = tk.Label(cont, image=err_img, bg=CARD_BG_COLOR)
            img_lbl.image = err_img
            img_lbl.pack(side=tk.LEFT, padx=(0, 15))
        
        # Text
        txt_fr = tk.Frame(cont, bg=CARD_BG_COLOR)
        txt_fr.pack(side=tk.LEFT)
        
        tk.Label(txt_fr, text="Oops!", font=SUBTITLE_FONT, fg=ACCENT_COLOR, 
                bg=CARD_BG_COLOR).pack(anchor="w")
        tk.Label(txt_fr, text=msg, font=BODY_FONT, fg=TEXT_COLOR, 
                bg=CARD_BG_COLOR, justify=tk.LEFT).pack(anchor="w", pady=(5, 0))
        
        # Buttons
        btn_fr = tk.Frame(self.popup, bg=CARD_BG_COLOR)
        btn_fr.place(relx=0.5, rely=0.85, anchor="center")
        
        if retry_cb:
            retry = tk.Label(btn_fr, text="Retry", font=(FONT_NAME, -14), fg=HIGHLIGHT_COLOR,
                            bg=ACCENT_COLOR, cursor="hand2", padx=20, pady=6)
            retry.pack(side=tk.LEFT, padx=(0, 10))
            retry.bind("<Button-1>", lambda e: self._retry(retry_cb))
        
        close = tk.Label(btn_fr, text="Close", font=(FONT_NAME, -14), fg=TEXT_COLOR,
                        bg=INPUT_BG_COLOR, cursor="hand2", padx=20, pady=6)
        close.pack(side=tk.LEFT)
        close.bind("<Button-1>", lambda e: self.close())
        
        return self.popup
    
    def _retry(self, cb):
        """Handle retry button click"""
        self.close()
        cb()
    
    def close(self):
        """Close error popup"""
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
    
    def _load_img(self, path, size):
        """Load and cache image"""
        key = f"{path}_{size}"
        if key in ErrorHandler._img_cache:
            return ErrorHandler._img_cache[key]
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            ErrorHandler._img_cache[key] = photo
            return photo
        except:
            return None