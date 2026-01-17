import tkinter as tk
from modules.constants import *
from modules.gif_player import GIFPlayer
from PIL import Image, ImageTk

# Shortcuts
BG = BG_COLOR
TXT = TEXT_COLOR


class HowToUseFrame(tk.Frame):
    """How To Use - Tutorial walkthroughs"""

    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG)
        self.ctrl = ctrl

        # State
        self.step = 0
        self.tut_type = None
        self.gif = None

        # Widgets
        self.wgts = []
        self.bg_lbl = None
        self.img_cache = {}

    # ==================== LIFECYCLE ====================

    def on_show(self):
        self._clean_menu()
        self._reset()
        self._clear_app_bg()
        self._show_menu()

    def _reset(self):
        self._stop_gif()
        self._destroy(self.wgts)
        if self.bg_lbl:
            self.bg_lbl.destroy()
            self.bg_lbl = None

        self.wgts = []
        self.step = 0
        self.tut_type = None

    def _clean_menu(self):
        menu = self.ctrl.frames.get("AppMenuFrame")
        if not menu:
            return
        for attr in ["btns", "lbls"]:
            if hasattr(menu, attr):
                self._destroy(getattr(menu, attr))
                setattr(menu, attr, [])

    def _clear_app_bg(self):
        """Stop and clear the main app's GIF background"""
        GIFPlayer.stop_all()
        if self.ctrl.gif:
            self.ctrl.gif.stop()
            self.ctrl.gif = None
        self.ctrl.bg_lbl.configure(image="")
        self.ctrl.bg_lbl.image = None

    # ==================== HELPERS ====================

    def _destroy(self, wlist):
        for w in wlist:
            try:
                w.destroy()
            except:
                pass

    def _load_img(self, path, size=None, resample=Image.LANCZOS):
        key = f"{path}_{size}_{resample}"
        if key in self.img_cache:
            return self.img_cache[key]
        try:
            img = Image.open(path)
            if size:
                img = img.resize(size, resample)
            photo = ImageTk.PhotoImage(img)
            self.img_cache[key] = photo
            return photo
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def _stop_gif(self):
        if self.gif:
            self.gif.stop()
            self.gif = None

    def _set_bg(self, path, is_gif=False):
        self._stop_gif()

        if self.bg_lbl:
            self.bg_lbl.destroy()
            self.bg_lbl = None

        self.bg_lbl = tk.Label(self.ctrl, bg=BG, bd=0, highlightthickness=0)
        self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        if is_gif:
            self.gif = GIFPlayer(self.bg_lbl, path, WINDOW_WIDTH, WINDOW_HEIGHT)
            self.gif.play()
        else:
            photo = self._load_img(path, (WINDOW_WIDTH, WINDOW_HEIGHT))
            if photo:
                self.bg_lbl.configure(image=photo)
                self.bg_lbl.image = photo

        for w in self.wgts:
            try:
                w.lift()
            except:
                pass

    # ==================== QUIT BUTTON ====================

    def _build_quit(self):
        photo = self._load_img(
            QUIT_BUTTON_IMG, (QUIT_BTN_WIDTH, QUIT_BTN_HEIGHT), Image.Resampling.BOX
        )
        if photo:
            btn = tk.Label(
                self.ctrl,
                image=photo,
                bg=BG,
                cursor="hand2",
                bd=0,
                highlightthickness=0,
            )
            btn.image = photo
            btn.place(x=QUIT_BTN_X, y=QUIT_BTN_Y)
            btn.bind("<Button-1>", lambda e: self._quit())
            btn.lift()
            self.wgts.append(btn)

    # ==================== TUTORIAL MENU ====================

    def _show_menu(self):
        self._destroy(self.wgts)
        self.wgts = []

        self._set_bg(TUT_MENU_BG)
        self._build_quit()

        apps = [
            {"name": "Pokédex", "icon": POKEDEX_ICON, "type": "pokedex"},
            {"name": "Team Builder", "icon": TEAM_BUILDER_ICON, "type": "team"},
        ]

        for i, app in enumerate(apps):
            self._add_icon(app, i)

    def _add_icon(self, app, idx):
        x = TUT_START_X + idx * TUT_SPACING_X
        y = TUT_START_Y

        photo = self._load_img(app["icon"], TUT_ICON_SIZE)
        if photo:
            btn = tk.Label(
                self.ctrl,
                image=photo,
                bg=HIGHLIGHT_COLOR,
                cursor="hand2",
                bd=0,
                highlightthickness=0,
            )
            btn.image = photo
            btn.place(x=x, y=y)
            btn.bind("<Button-1>", lambda e, t=app["type"]: self._start_tut(t))
            btn.lift()
            self.wgts.append(btn)

        lbl = tk.Label(
            self.ctrl,
            text=app["name"],
            font=SUBTITLE_FONT,
            fg=BG_COLOR,
            bg=HIGHLIGHT_COLOR,
        )
        lbl.place(x=x + TUT_LABEL_OFFSET_X, y=y + TUT_LABEL_OFFSET_Y, anchor="center")
        lbl.lift()
        self.wgts.append(lbl)

    # ==================== TUTORIAL FLOW ====================

    def _start_tut(self, tut_type):
        self.tut_type = tut_type
        self.step = 0
        self._show_step()

    def _show_step(self):
        self._destroy(self.wgts)
        self.wgts = []

        if self.tut_type == "pokedex":
            self._show_poke_step()
        elif self.tut_type == "team":
            self._show_team_step()

    def _show_poke_step(self):
        if self.step >= len(POKE_TUT):
            self._show_menu()
            return

        path = POKE_TUT[self.step]
        loc, is_gif = POKE_TUT_CFG[self.step]

        self._set_bg(path, is_gif)
        self._build_nav(loc)

    def _show_team_step(self):
        if self.step >= len(TEAM_TUT):
            self._show_menu()
            return

        path = TEAM_TUT[self.step]
        loc, is_gif = TEAM_TUT_CFG[self.step]

        self._set_bg(path, is_gif)
        self._build_nav(loc)

    def _build_nav(self, loc):
        if self.tut_type == "pokedex":
            total = len(POKE_TUT)
        elif self.tut_type == "team":
            total = len(TEAM_TUT)
        else:
            total = 0

        is_first = self.step == 0
        is_last = self.step == total - 1

        if loc == 1:
            self._build_loc1(is_first, is_last)
        elif loc == 2:
            self._build_loc2(is_first, is_last)
        elif loc == 3:
            self._build_loc3()

    # ==================== NAVIGATION BUTTONS ====================

    def _build_nav(self, loc):
        total = len(POKE_TUT) if self.tut_type == "pokedex" else 0
        is_first = self.step == 0
        is_last = self.step == total - 1

        if loc == 1:
            self._build_loc1(is_first, is_last)
        elif loc == 2:
            self._build_loc2(is_first, is_last)
        elif loc == 3:
            self._build_loc3()

    def _build_loc1(self, is_first, is_last):
        if not is_last:
            nxt = tk.Label(
                self.ctrl,
                text="Next ↑",
                font=TUT_BTN_FONT,
                fg=HIGHLIGHT_COLOR,
                bg=ACCENT_COLOR,
                cursor="hand2",
                padx=TUT_BTN_PAD_X,
                pady=TUT_BTN_PAD_Y,
            )
            nxt.place(x=TUT_LOC1_X, y=TUT_LOC1_NEXT_Y)
            nxt.bind("<Button-1>", lambda e: self._next())
            nxt.lift()
            self.wgts.append(nxt)

        if not is_first:
            prv = tk.Label(
                self.ctrl,
                text="Prev ↓",
                font=TUT_BTN_FONT,
                fg=HIGHLIGHT_COLOR,
                bg=ACCENT_COLOR,
                cursor="hand2",
                padx=TUT_BTN_PAD_X,
                pady=TUT_BTN_PAD_Y,
            )
            prv.place(x=TUT_LOC1_X, y=TUT_LOC1_PREV_Y)
            prv.bind("<Button-1>", lambda e: self._prev())
            prv.lift()
            self.wgts.append(prv)

    def _build_loc2(self, is_first, is_last):
        if not is_last:
            nxt = tk.Label(
                self.ctrl,
                text="Next ↑",
                font=TUT_BTN_FONT,
                fg=HIGHLIGHT_COLOR,
                bg=ACCENT_COLOR,
                cursor="hand2",
                padx=TUT_BTN_PAD_X,
                pady=TUT_BTN_PAD_Y,
            )
            nxt.place(x=TUT_LOC2_X, y=TUT_LOC2_NEXT_Y)
            nxt.bind("<Button-1>", lambda e: self._next())
            nxt.lift()
            self.wgts.append(nxt)

        if not is_first:
            prv = tk.Label(
                self.ctrl,
                text="Prev ↓",
                font=TUT_BTN_FONT,
                fg=HIGHLIGHT_COLOR,
                bg=ACCENT_COLOR,
                cursor="hand2",
                padx=TUT_BTN_PAD_X,
                pady=TUT_BTN_PAD_Y,
            )
            prv.place(x=TUT_LOC2_X, y=TUT_LOC2_PREV_Y)
            prv.bind("<Button-1>", lambda e: self._prev())
            prv.lift()
            self.wgts.append(prv)

    def _build_loc3(self):
        rpt = tk.Label(
            self.ctrl,
            text="↻ Repeat",
            font=TUT_BTN_FONT,
            fg=HIGHLIGHT_COLOR,
            bg=ACCENT_COLOR,
            cursor="hand2",
            padx=TUT_BTN_PAD_X,
            pady=TUT_BTN_PAD_Y,
        )
        rpt.place(x=TUT_LOC3_X, y=TUT_LOC3_Y)
        rpt.bind("<Button-1>", lambda e: self._repeat())
        rpt.lift()
        self.wgts.append(rpt)

        ext = tk.Label(
            self.ctrl,
            text="Exit ✕",
            font=TUT_BTN_FONT,
            fg=HIGHLIGHT_COLOR,
            bg=INPUT_BG_COLOR,
            cursor="hand2",
            padx=TUT_BTN_PAD_X,
            pady=TUT_BTN_PAD_Y,
        )
        ext.place(x=TUT_LOC3_X + TUT_LOC3_SPACING, y=TUT_LOC3_Y)
        ext.bind("<Button-1>", lambda e: self._exit_tut())
        ext.lift()
        self.wgts.append(ext)

    def _next(self):
        self.step += 1
        self._show_step()

    def _prev(self):
        if self.step > 0:
            self.step -= 1
        self._show_step()

    def _repeat(self):
        self.step = 0
        self._show_step()

    def _exit_tut(self):
        self._reset()
        self._show_menu()

    # ==================== QUIT ====================

    def _quit(self):
        self._stop_gif()
        self._reset()
        self.ctrl.show("AppMenuFrame")
