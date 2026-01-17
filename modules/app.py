"""
Project Rotom - Main Application Class
"""

import tkinter as tk
from modules.constants import *
from modules.gif_player import GIFPlayer


class App(tk.Tk):
    """Main application - manages frames and window"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Project Rotom")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        
        self.cur_frame = None
        self.gif = None
        self.frames = {}
        
        self.bg_lbl = tk.Label(self, bg=BG_COLOR)
        self.bg_lbl.pack(fill="both", expand=True)
        
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self._init_frames()
        self.show("WelcomeFrame")
    
    def _init_frames(self):
        """Initialize all frames"""
        from frames.welcome import WelcomeFrame
        from frames.app_menu import AppMenuFrame
        from frames.how_to_use import HowToUseFrame
        from frames.pokedex import PokedexFrame
        from frames.team_builder import TeamBuilderFrame
        
        for F in (WelcomeFrame, AppMenuFrame, HowToUseFrame, PokedexFrame, TeamBuilderFrame):
            f = F(self.container, self)
            self.frames[F.__name__] = f
            f.grid(row=0, column=0, sticky="nsew")
    
    def show(self, name):
        """Show a frame by name"""
        if self.gif:
            self.gif.stop()
        
        frame = self.frames[name]
        frame.tkraise()
        self.container.lift()
        self.cur_frame = name
        
        if hasattr(frame, 'on_show'):
            frame.on_show()
    
    def set_bg(self, path):
        """Set background GIF"""
        GIFPlayer.stop_all()
        self.gif = GIFPlayer(self.bg_lbl, path, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.gif.play()


if __name__ == "__main__":
    App().mainloop()