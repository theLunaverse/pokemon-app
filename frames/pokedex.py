import tkinter as tk
from modules.constants import *
from modules.pokeapi import (
    get_pokemon, get_pokemon_by_type, search_pokemon_by_name,
    get_type_icon_url, get_pokemon_description, get_pokemon_weaknesses, 
    get_evolution_chain, NetworkError, PokeAPIError
)
from modules.error_handler import ErrorHandler
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Shortcuts
BG = BG_COLOR
CARD_BG = CARD_BG_COLOR
TXT = TEXT_COLOR


class PokedexFrame(tk.Frame):
    """Pokédex frame - Search and browse Pokémon"""
    
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG)
        self.ctrl = ctrl
        self.err = ErrorHandler(ctrl)
        
        # State
        self.filtered = []
        self.page = 0
        self.sel_types = {}
        self.in_detail = False
        self.shiny = False
        self.cur_poke = None
        
        # Widgets
        self.wgts = []
        self.filter_fr = None
        self.back_btn = None
        self.search_ent = None
        self.sprite_lbl = None
        self.shiny_btn = None
        
        # Caches
        self.type_cache = {}
        self.img_cache = {}
        self.anim_cache = {}
        self.shiny_cache = {}
    
    # ==================== LIFECYCLE ====================
    
    def on_show(self):
        self._clean_menu()
        self._reset()
        self._build()
        self.ctrl.set_bg(ROTOM_PHONE_BG)
        self._init_list()
    
    def _init_list(self):
        try:
            self.filtered = list(range(1, TOTAL_POKEMON + 1))
            self._show_page()
        except NetworkError as e:
            self.wgts.append(self.err.show(str(e), self._init_list))
        except PokeAPIError as e:
            self.wgts.append(self.err.show(str(e)))
    
    def _reset(self):
        self._stop_all()
        self.err.close()
        self._destroy(self.wgts)
        if self.back_btn:
            self.back_btn.destroy()
        
        self.wgts = []
        self.filtered = []
        self.page = 0
        self.sel_types = {}
        self.filter_fr = None
        self.back_btn = None
        self.in_detail = False
        self.shiny = False
        self.cur_poke = None
        self.sprite_lbl = None
        self.shiny_btn = None
    
    def _clean_menu(self):
        menu = self.ctrl.frames.get('AppMenuFrame')
        if not menu:
            return
        for attr in ['btns', 'lbls']:
            if hasattr(menu, attr):
                self._destroy(getattr(menu, attr))
                setattr(menu, attr, [])
    
    # ==================== HELPERS ====================
    
    def _destroy(self, wlist):
        for w in wlist:
            try: w.destroy()
            except: pass
    
    def _load_img(self, path, size, resample=Image.NEAREST):
        key = f"{path}_{size}_{resample}"
        if key in self.img_cache:
            return self.img_cache[key]
        try:
            img = Image.open(path).resize(size, resample)
            photo = ImageTk.PhotoImage(img)
            self.img_cache[key] = photo
            return photo
        except:
            return None
    
    def _fetch(self, url, size, fallback=False):
        """Fetch image from URL. If fallback=True, return error.png on failure"""
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).resize(size, Image.NEAREST)
            return ImageTk.PhotoImage(img)
        except:
            if fallback:
                return self._load_img(ERROR_IMG, size)
            return None
    
    def _type_icon(self, name):
        if name in self.type_cache:
            return self.type_cache[name]
        try:
            url = get_type_icon_url(name)
            if not url:
                return None
            photo = self._fetch(url, TYPE_ICON_SIZE, fallback=False)
            if photo:
                self.type_cache[name] = photo
            return photo
        except:
            return None
    
    def _click_lbl(self, parent, img, x, y, cb):
        if not img:
            return None
        lbl = tk.Label(parent, image=img, bg=BG, cursor="hand2", bd=0, highlightthickness=0)
        lbl.image = img
        lbl.place(x=x, y=y)
        lbl.bind("<Button-1>", lambda e: cb())
        return lbl
    
    # ==================== ANIMATION ====================
    
    def _get_anim(self, pid, size, shiny=False):
        cache = self.shiny_cache if shiny else self.anim_cache
        prefix = "shiny_" if shiny else ""
        key = f"{prefix}{pid}_{size}"
        
        if key in cache:
            return cache[key]
        
        if pid > MAX_ANIMATED_ID:
            return None
        
        base_url = SHINY_ANIMATED_SPRITE_URL if shiny else ANIMATED_SPRITE_URL
        url = f"{base_url}/{pid}.gif"
        
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            
            gif = Image.open(BytesIO(r.content))
            frames, durs = [], []
            
            try:
                while True:
                    frames.append(ImageTk.PhotoImage(gif.copy().resize(size, Image.NEAREST)))
                    durs.append(gif.info.get('duration', 100))
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
            
            if frames:
                data = {'frames': frames, 'durations': durs}
                cache[key] = data
                return data
        except:
            pass
        return None
    
    def _animate(self, lbl):
        if not hasattr(lbl, 'frames') or not lbl.winfo_exists():
            return
        
        frame = lbl.frames[lbl.cur_frame]
        lbl.configure(image=frame)
        lbl.image = frame
        
        lbl.cur_frame = (lbl.cur_frame + 1) % len(lbl.frames)
        dur = lbl.durs[lbl.cur_frame] if lbl.cur_frame < len(lbl.durs) else 100
        lbl.after_id = lbl.after(dur, lambda: self._animate(lbl))
    
    def _start_anim(self, lbl, data, static=None):
        lbl.frames = data['frames']
        lbl.durs = data['durations']
        lbl.cur_frame = 0
        if static:
            lbl.static = static
        self._animate(lbl)
    
    def _stop_anim(self, lbl):
        if hasattr(lbl, 'after_id'):
            try:
                lbl.after_cancel(lbl.after_id)
                del lbl.after_id
            except: pass
        
        if hasattr(lbl, 'static') and lbl.static:
            lbl.configure(image=lbl.static)
            lbl.image = lbl.static
        
        for attr in ['frames', 'durs', 'cur_frame']:
            if hasattr(lbl, attr):
                delattr(lbl, attr)
    
    def _stop_all(self):
        for w in self.wgts:
            try:
                if hasattr(w, 'after_id'):
                    w.after_cancel(w.after_id)
                if w.winfo_exists() and hasattr(w, 'winfo_children'):
                    for child in w.winfo_children():
                        if hasattr(child, 'after_id'):
                            try:
                                child.after_cancel(child.after_id)
                            except:
                                pass
            except:
                pass
    
    def _load_sprite(self, poke, lbl, size=DETAIL_SPRITE_SIZE):
        data = self._get_anim(poke['id'], size)
        if data:
            self._start_anim(lbl, data)
        else:
            photo = self._fetch(poke['sprite_url'], size, fallback=True)
            if photo:
                lbl.configure(image=photo)
                lbl.image = photo
    
    def _load_detail_sprite(self, poke, lbl, size=DETAIL_SPRITE_SIZE):
        pid = poke['id']
        
        if self.shiny:
            data = self._get_anim(pid, size, shiny=True)
            if data:
                self._start_anim(lbl, data)
                return
            url = poke.get('sprite_shiny_url')
            if url:
                photo = self._fetch(url, size, fallback=True)
                if photo:
                    lbl.configure(image=photo)
                    lbl.image = photo
                    return
        else:
            data = self._get_anim(pid, size)
            if data:
                self._start_anim(lbl, data)
                return
            photo = self._fetch(poke['sprite_url'], size, fallback=True)
            if photo:
                lbl.configure(image=photo)
                lbl.image = photo
    
    def _toggle_shiny(self):
        if not self.cur_poke or not self.sprite_lbl:
            return
        self._stop_anim(self.sprite_lbl)
        self.shiny = not self.shiny
        self.shiny_btn.configure(fg=GOLD_COLOR if self.shiny else MUTED_COLOR)
        self._load_detail_sprite(self.cur_poke, self.sprite_lbl)
    
    # ==================== UI BUILDING ====================
    
    def _build(self):
        photo = self._load_img(QUIT_BUTTON_IMG, (QUIT_BTN_WIDTH, QUIT_BTN_HEIGHT))
        quit_btn = self._click_lbl(self.ctrl, photo, QUIT_BTN_X, QUIT_BTN_Y, self._quit)
        if quit_btn:
            self.wgts.append(quit_btn)
        
        self._build_search()
        
        photo = self._load_img(BACK_BUTTON_IMG, BACK_BTN_SIZE, Image.Resampling.BOX)
        if photo:
            self.back_btn = tk.Label(self.ctrl, image=photo, bg=BG, cursor="hand2", bd=0, highlightthickness=0)
            self.back_btn.image = photo
        
        self._build_filter()
    
    def _build_search(self):
        fr = tk.Frame(self.ctrl, bg=BG)
        fr.place(x=SEARCH_X, y=SEARCH_Y, width=SEARCH_WIDTH, height=SEARCH_HEIGHT)
        self.wgts.append(fr)
        
        tk.Label(fr, text="Search:", font=BODY_FONT, fg=TXT, bg=BG).pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_ent = tk.Entry(fr, font=BODY_FONT, width=25, bg=INPUT_BG_COLOR, 
                                   fg=TXT, insertbackground=TXT, relief=tk.FLAT)
        self.search_ent.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        self.search_ent.bind("<Return>", lambda e: self._search())
        
        btn = tk.Label(fr, text="Search", font=SEARCH_BTN_FONT, fg=HIGHLIGHT_COLOR, 
                      bg=ACCENT_COLOR, cursor="hand2", padx=15, pady=8)
        btn.pack(side=tk.LEFT, padx=(0, 10))
        btn.bind("<Button-1>", lambda e: self._search())
    
    def _build_filter(self):
        self.filter_fr = tk.Frame(self.ctrl, bg=BG)
        self.filter_fr.place(x=FILTER_X, y=FILTER_Y, width=FILTER_WIDTH, height=FILTER_HEIGHT)
        self.wgts.append(self.filter_fr)
        
        row1 = tk.Frame(self.filter_fr, bg=BG)
        row1.pack(pady=(0, 2))
        row2 = tk.Frame(self.filter_fr, bg=BG)
        row2.pack()
        
        for i, t in enumerate(POKEMON_TYPES):
            var = tk.BooleanVar(value=False)
            self.sel_types[t] = var
            cb = tk.Checkbutton(
                row1 if i < TYPES_PER_ROW else row2, text=t, variable=var,
                font=FILTER_FONT, fg=TXT, bg=BG,
                selectcolor=INPUT_BG_COLOR, activebackground=BG,
                activeforeground=TXT, cursor="hand2",
                command=self._on_filter
            )
            cb.pack(side=tk.LEFT, padx=2)
    
    # ==================== FILTER & SEARCH ====================
    
    def _on_filter(self):
        self.page = 0
        self._apply_filter()
    
    def _apply_filter(self):
        sel = [t for t, v in self.sel_types.items() if v.get()]
        
        if not sel:
            self.filtered = list(range(1, TOTAL_POKEMON + 1))
            self._show_page()
            return
        
        try:
            ids = set()
            for t in sel:
                for p in get_pokemon_by_type(t):
                    pid = p.get('id')
                    if pid and pid <= TOTAL_POKEMON:
                        ids.add(pid)
            self.filtered = sorted(list(ids))
            self._show_page()
        except NetworkError as e:
            self.wgts.append(self.err.show(str(e), self._apply_filter))
        except PokeAPIError as e:
            self.wgts.append(self.err.show(str(e)))
    
    def _search(self):
        q = self.search_ent.get().strip().lower()
        
        if not q:
            self._back_list()
            return
        
        if q.isdigit():
            pid = int(q)
            if 1 <= pid <= TOTAL_POKEMON:
                self.filtered = [pid]
                self.page = 0
                self._show_back()
                self.filter_fr.place_forget()
                self._show_page()
                return
        
        try:
            ids = search_pokemon_by_name(q)
            self.filtered = ids if ids else []
            self.page = 0
            self._show_back()
            self.filter_fr.place_forget()
            self._show_page()
        except NetworkError as e:
            self.wgts.append(self.err.show(str(e), self._search))
        except PokeAPIError as e:
            self.wgts.append(self.err.show(str(e)))
    
    def _back_list(self):
        self.search_ent.delete(0, tk.END)
        self.page = 0
        if self.back_btn:
            self.back_btn.place_forget()
        self.filter_fr.place(x=FILTER_X, y=FILTER_Y, width=FILTER_WIDTH, height=FILTER_HEIGHT)
        
        for v in self.sel_types.values():
            v.set(False)
        
        self._apply_filter()
    
    def _show_back(self):
        if self.back_btn:
            self.back_btn.bind("<Button-1>", lambda e: self._back_list())
            self.back_btn.place(x=BACK_BTN_X, y=BACK_BTN_Y)
    
    # ==================== DISPLAY ====================
    
    def _show_page(self):
        self._stop_all()
        self._destroy(self.wgts[3:])
        self.wgts = self.wgts[:3]
        
        if not self.filtered:
            self._no_results()
            return
        
        start = self.page * CARDS_PER_PAGE
        items = self.filtered[start:start + CARDS_PER_PAGE]
        
        for i, item in enumerate(items):
            try:
                poke = get_pokemon(item) if isinstance(item, int) else item
                if poke:
                    self._card(poke, i)
            except NetworkError as e:
                self.wgts.append(self.err.show(str(e), self._show_page))
                return
            except PokeAPIError as e:
                self.wgts.append(self.err.show(str(e)))
                return
        
        self._nav_btns()
    
    def _card(self, poke, idx):
        x = CARD_START_X + (idx % 3) * CARD_SPACING_X
        y = CARD_START_Y + (idx // 3) * CARD_SPACING_Y
        
        card = tk.Frame(self.ctrl, bg=CARD_BG, width=CARD_WIDTH, height=CARD_HEIGHT, cursor="hand2",
                       highlightbackground=CARD_BG, highlightcolor=HIGHLIGHT_COLOR, highlightthickness=3)
        card.pack_propagate(False)
        card.place(x=x, y=y)
        self.wgts.append(card)
        
        detail = lambda e, p=poke: self._detail(p)
        card.bind("<Button-1>", detail)
        card.bind("<Enter>", lambda e: card.configure(highlightbackground=HIGHLIGHT_COLOR))
        card.bind("<Leave>", lambda e: card.configure(highlightbackground=CARD_BG))
        
        photo = self._fetch(poke['sprite_url'], CARD_SPRITE_SIZE, fallback=True)
        if photo:
            spr = tk.Label(card, image=photo, bg=CARD_BG, width=CARD_SPRITE_SIZE[0], height=CARD_SPRITE_SIZE[1])
            spr.image = photo
            spr.pack(pady=8)
            spr.bind("<Button-1>", detail)
            
            if poke['id'] <= MAX_ANIMATED_ID:
                spr.bind("<Enter>", lambda e, p=poke, l=spr, img=photo: self._card_enter(p, l, img, card))
                spr.bind("<Leave>", lambda e, l=spr: self._card_leave(l, card))
        
        row = tk.Frame(card, bg=CARD_BG)
        row.pack(pady=(5, 0))
        
        lbl = tk.Label(row, text=poke['name'], font=POKE_NAME_FONT, fg=TXT, bg=CARD_BG)
        lbl.pack(side=tk.LEFT, padx=(0, 8))
        lbl.bind("<Button-1>", detail)
        
        lbl = tk.Label(row, text=f"#{poke['id']}", font=POKE_ID_FONT, fg=MUTED_COLOR, bg=CARD_BG)
        lbl.pack(side=tk.LEFT)
        lbl.bind("<Button-1>", detail)
        
        row = tk.Frame(card, bg=CARD_BG)
        row.pack(pady=(8, 0))
        
        for t in poke.get('types', []):
            icon = self._type_icon(t)
            if icon:
                lbl = tk.Label(row, image=icon, bg=CARD_BG)
                lbl.image = icon
                lbl.pack(side=tk.LEFT, padx=3)
                lbl.bind("<Button-1>", detail)
    
    def _card_enter(self, poke, lbl, static, card):
        data = self._get_anim(poke['id'], CARD_ANIM_SIZE)
        if data:
            self._start_anim(lbl, data, static)
        card.configure(highlightbackground=HIGHLIGHT_COLOR)
    
    def _card_leave(self, lbl, card):
        self._stop_anim(lbl)
        card.configure(highlightbackground=CARD_BG)
    
    def _no_results(self):
        fr = tk.Frame(self.ctrl, bg=CARD_BG, width=400, height=100)
        fr.pack_propagate(False)
        fr.place(x=345, y=350)
        self.wgts.append(fr)
        
        tk.Label(fr, text="No Pokémon found!\nTry searching for something else.",
                font=BODY_FONT, fg=TXT, bg=CARD_BG, justify=tk.CENTER
                ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _nav_btns(self):
        total = (len(self.filtered) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
        
        if total <= 1:
            return
        
        if self.page > 0:
            btn = tk.Label(self.ctrl, text="← Previous", font=NAV_FONT,
                          fg=HIGHLIGHT_COLOR, bg=ACCENT_COLOR, cursor="hand2", padx=10, pady=5)
            btn.place(x=PREV_BTN_X, y=NAV_BTN_Y)
            btn.bind("<Button-1>", lambda e: self._page(-1))
            self.wgts.append(btn)
        
        if self.page < total - 1:
            btn = tk.Label(self.ctrl, text="Next →", font=NAV_FONT,
                          fg=HIGHLIGHT_COLOR, bg=ACCENT_COLOR, cursor="hand2", padx=10, pady=5)
            btn.place(x=NEXT_BTN_X, y=NAV_BTN_Y)
            btn.bind("<Button-1>", lambda e: self._page(1))
            self.wgts.append(btn)
        
        lbl = tk.Label(self.ctrl, text=f"Page {self.page + 1} of {total}",
                      font=NAV_FONT, fg=TXT, bg=BG)
        lbl.place(x=PAGE_LBL_X, y=PAGE_LBL_Y)
        self.wgts.append(lbl)
    
    def _page(self, delta):
        self._stop_all()
        self.page += delta
        self._show_page()
    
    # ==================== DETAIL VIEW ====================
    
    def _detail(self, poke):
        self._stop_all()
        self.in_detail = True
        self.shiny = False
        self.cur_poke = poke
        
        self.wgts[1].place_forget()
        self.filter_fr.place_forget()
        
        self._destroy(self.wgts[3:])
        self.wgts = self.wgts[:3]
        
        self._left_card(poke)
        self._right_card(poke)
        
        if self.back_btn:
            self.back_btn.bind("<Button-1>", lambda e: self._close_detail())
            self.back_btn.place(x=BACK_BTN_X, y=BACK_BTN_Y)
    
    def _left_card(self, poke):
        card = tk.Frame(self.ctrl, bg=CARD_BG, width=DETAIL_CARD_LEFT_WIDTH, height=DETAIL_CARD_HEIGHT)
        card.pack_propagate(False)
        card.place(x=DETAIL_LEFT_X, y=DETAIL_Y)
        self.wgts.append(card)
        
        self.shiny_btn = tk.Label(card, text="◆", font=SHINY_BTN_FONT,
                                  fg=MUTED_COLOR, bg=INPUT_BG_COLOR, width=2, height=1,
                                  cursor="hand2", relief=tk.FLAT)
        self.shiny_btn.place(x=SHINY_BTN_X, y=SHINY_BTN_Y)
        
        def enter(e):
            self.shiny_btn.configure(fg=GOLD_COLOR if not self.shiny else MUTED_COLOR, bg=HOVER_BG_COLOR)
        def leave(e):
            self.shiny_btn.configure(fg=GOLD_COLOR if self.shiny else MUTED_COLOR, bg=INPUT_BG_COLOR)
        
        self.shiny_btn.bind("<Enter>", enter)
        self.shiny_btn.bind("<Leave>", leave)
        self.shiny_btn.bind("<Button-1>", lambda e: self._toggle_shiny())
        
        self.sprite_lbl = tk.Label(card, bg=CARD_BG)
        self.sprite_lbl.pack(pady=(30, 10))
        self._load_detail_sprite(poke, self.sprite_lbl)
        
        row = tk.Frame(card, bg=CARD_BG)
        row.pack(pady=(10, 0))
        tk.Label(row, text=poke['name'], font=POKE_DETAIL_NAME_FONT, fg=TXT, bg=CARD_BG
                ).pack(side=tk.LEFT, padx=(0, 15))
        tk.Label(row, text=f"#{poke['id']}", font=POKE_DETAIL_ID_FONT, fg=MUTED_COLOR, bg=CARD_BG
                ).pack(side=tk.LEFT)
        
        row = tk.Frame(card, bg=CARD_BG)
        row.pack(pady=(20, 0))
        for t in poke.get('types', []):
            icon = self._type_icon(t)
            if icon:
                lbl = tk.Label(row, image=icon, bg=CARD_BG)
                lbl.image = icon
                lbl.pack(side=tk.LEFT, padx=8)
    
    def _right_card(self, poke):
        card = tk.Frame(self.ctrl, bg=CARD_BG, width=DETAIL_CARD_RIGHT_WIDTH, height=DETAIL_CARD_HEIGHT)
        card.pack_propagate(False)
        card.place(x=DETAIL_RIGHT_X, y=DETAIL_Y)
        self.wgts.append(card)
        
        desc = get_pokemon_description(poke['id'])
        if desc:
            if len(desc) > DESC_MAX_LEN:
                desc = desc[:DESC_MAX_LEN - 3] + "..."
            tk.Label(card, text=desc, font=SECTION_FONT, fg=TXT, bg=CARD_BG,
                    wraplength=360, justify=tk.LEFT).pack(pady=(20, 10), padx=20, anchor="w")
        
        self._weak_section(card, poke)
        self._evo_section(card, poke)
    
    def _weak_section(self, parent, poke):
        weak = get_pokemon_weaknesses(poke.get('types', []))
        if not weak:
            return
        
        fr = tk.Frame(parent, bg=CARD_BG)
        fr.pack(pady=(10, 5), padx=20, anchor="w", fill="x")
        
        tk.Label(fr, text="Weak to:", font=SECTION_FONT, fg=TXT, bg=CARD_BG).pack(anchor="w")
        
        row = None
        for i, t in enumerate(weak):
            if i % WEAK_PER_ROW == 0:
                row = tk.Frame(fr, bg=CARD_BG)
                row.pack(anchor="w", pady=(2, 0))
            
            icon = self._type_icon(t)
            if icon:
                lbl = tk.Label(row, image=icon, bg=CARD_BG)
                lbl.image = icon
                lbl.pack(side=tk.LEFT, padx=2)
    
    def _evo_section(self, parent, poke):
        evos = get_evolution_chain(poke['id'])
        if len(evos) <= 1:
            return
        
        cont = tk.Frame(parent, bg=CARD_BG)
        cont.pack(pady=(15, 10), padx=20, anchor="w", fill="x")
        
        tk.Label(cont, text="Evolution:", font=SECTION_FONT, fg=TXT, bg=CARD_BG).pack(anchor="w")
        
        cfr = tk.Frame(cont, bg=CARD_BG, height=100)
        cfr.pack(fill="x", pady=(5, 0))
        
        canvas = tk.Canvas(cfr, bg=CARD_BG, height=90, highlightthickness=0)
        scroll = tk.Scrollbar(cfr, orient="horizontal", command=canvas.xview)
        inner = tk.Frame(canvas, bg=CARD_BG)
        
        canvas.configure(xscrollcommand=scroll.set)
        canvas.pack(side=tk.TOP, fill="x")
        scroll.pack(side=tk.BOTTOM, fill="x")
        canvas.create_window((0, 0), window=inner, anchor="nw")
        
        for i, evo in enumerate(evos):
            self._evo_sprite(inner, evo, poke['id'], i)
        
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        if inner.winfo_reqwidth() <= 360:
            scroll.pack_forget()
    
    def _evo_sprite(self, parent, evo, cur_id, idx):
        fr = tk.Frame(parent, bg=CARD_BG)
        fr.pack(side=tk.LEFT, padx=5)
        
        if idx > 0:
            tk.Label(fr, text="→", font=ARROW_FONT, fg=MUTED_COLOR, bg=CARD_BG
                    ).pack(side=tk.LEFT, padx=(0, 5))
        
        cont = tk.Frame(fr, bg=CARD_BG, highlightbackground=CARD_BG, highlightthickness=2)
        cont.pack(side=tk.LEFT)
        
        photo = self._fetch(evo['sprite_url'], EVO_SPRITE_SIZE, fallback=True)
        if photo:
            is_cur = evo['id'] == cur_id
            hl = GOLD_COLOR if is_cur else CARD_BG
            
            spr = tk.Label(cont, image=photo, bg=CARD_BG, cursor="arrow" if is_cur else "hand2",
                          highlightbackground=hl, highlightthickness=2)
            spr.image = photo
            spr.pack(padx=3, pady=3)
            
            name = tk.Label(cont, text=evo['name'], font=EVO_NAME_FONT,
                           fg=GOLD_COLOR if is_cur else TXT, bg=CARD_BG,
                           cursor="arrow" if is_cur else "hand2")
            name.pack(pady=(0, 3))
            
            if not is_cur:
                def enter(e, c=cont, s=spr, n=name):
                    c.configure(highlightbackground=HIGHLIGHT_COLOR)
                    s.configure(highlightbackground=HIGHLIGHT_COLOR, bg=INPUT_BG_COLOR)
                    n.configure(fg=HIGHLIGHT_COLOR, bg=INPUT_BG_COLOR)
                
                def leave(e, c=cont, s=spr, n=name):
                    c.configure(highlightbackground=CARD_BG)
                    s.configure(highlightbackground=CARD_BG, bg=CARD_BG)
                    n.configure(fg=TXT, bg=CARD_BG)
                
                def click(e, ev=evo):
                    self._switch(ev)
                
                for w in [cont, spr, name]:
                    w.bind("<Enter>", enter)
                    w.bind("<Leave>", leave)
                    w.bind("<Button-1>", click)
    
    def _switch(self, evo):
        try:
            poke = get_pokemon(evo['id'])
            if not poke:
                return
            self._stop_all()
            self.shiny = False
            self.cur_poke = poke
            
            self._destroy(self.wgts[3:])
            self.wgts = self.wgts[:3]
            
            self._left_card(poke)
            self._right_card(poke)
        except NetworkError as e:
            self.wgts.append(self.err.show(str(e), lambda: self._switch(evo)))
        except PokeAPIError as e:
            self.wgts.append(self.err.show(str(e)))
    
    def _close_detail(self):
        self.in_detail = False
        self.shiny = False
        self.cur_poke = None
        self.sprite_lbl = None
        self.shiny_btn = None
        self._stop_all()
        
        self._destroy(self.wgts[3:])
        self.wgts = self.wgts[:3]
        
        self.search_ent.delete(0, tk.END)
        for v in self.sel_types.values():
            v.set(False)
        
        self.wgts[1].place(x=SEARCH_X, y=SEARCH_Y, width=SEARCH_WIDTH, height=SEARCH_HEIGHT)
        self.filter_fr.place(x=FILTER_X, y=FILTER_Y, width=FILTER_WIDTH, height=FILTER_HEIGHT)
        if self.back_btn:
            self.back_btn.place_forget()
        
        self.filtered = list(range(1, TOTAL_POKEMON + 1))
        self.page = 0
        self._show_page()
    
    # ==================== QUIT ====================
    
    def _quit(self):
        self._stop_all()
        self.err.close()
        self._reset()
        self.ctrl.show("AppMenuFrame")