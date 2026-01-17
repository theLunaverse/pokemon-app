import tkinter as tk
from modules.constants import *
from modules.pokeapi import (
    get_pokemon, get_all_pokemon_names, get_pokemon_weaknesses,
    NetworkError, PokeAPIError
)
from modules.error_handler import ErrorHandler
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random

# Shortcuts
BG = BG_COLOR
CARD_BG = CARD_BG_COLOR
TXT = TEXT_COLOR


class TeamBuilderFrame(tk.Frame):
    """Team Builder - Create and analyze teams"""
    
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG)
        self.ctrl = ctrl
        self.err = ErrorHandler(ctrl)
        
        # State
        self.team = [None] * 6
        self.cards = []
        self.dd_open = None
        self.dd_wgts = []
        self.dd_cvs = None
        self.dd_idx = None
        self.poke_list_fr = None
        self.all_pokes = []
        self.filt_pokes = []
        
        # Widgets
        self.wgts = []
        self.ana_popup = None
        self.stat_bars = []
        
        # Caches
        self.img_cache = {}
        self.spr_cache = {}
    
    # ==================== LIFECYCLE ====================

    def on_show(self):
        self._clean_menu()
        self._reset()
        self._build()
        self.ctrl.set_bg(ROTOM_PHONE_BG)
        self._load_poke_list()

    def _reset(self):
        self._close_dd()
        self._close_ana()
        self.err.close()
        self._destroy(self.wgts)
        
        self.wgts = []
        self.cards = []
        self.team = [None] * 6
        self.dd_open = None
        self.dd_cvs = None
        self.dd_idx = None
        self.poke_list_fr = None
        self.stat_bars = []

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
    
    def _load_img(self, path, size, resample=Image.LANCZOS):
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
        key = f"{url}_{size}"
        if key in self.spr_cache:
            return self.spr_cache[key]
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).resize(size, Image.NEAREST)
            photo = ImageTk.PhotoImage(img)
            self.spr_cache[key] = photo
            return photo
        except:
            if fallback:
                return self._load_img(ERROR_IMG, size)
            return None
    
    def _load_poke_list(self):
        if not self.all_pokes:
            try:
                self.all_pokes = get_all_pokemon_names()
            except NetworkError as e:
                self.wgts.append(self.err.show(str(e), self._load_poke_list))
                return
            except PokeAPIError as e:
                self.wgts.append(self.err.show(str(e)))
                return
        self.filt_pokes = self.all_pokes.copy()

    def _type_icon(self, name):
        key = f"type_{name}"
        if key in self.img_cache:
            return self.img_cache[key]
        try:
            tid = TYPE_IDS.get(name.lower())
            if not tid:
                return None
            url = f"{TYPE_ICON_URL}/{tid}.png"
            photo = self._fetch(url, TYPE_ICON_SIZE, fallback=False)
            if photo:
                self.img_cache[key] = photo
            return photo
        except:
            return None
    
    # ==================== UI BUILDING ====================
    
    def _build(self):
        photo = self._load_img(QUIT_BUTTON_IMG, (QUIT_BTN_WIDTH, QUIT_BTN_HEIGHT), Image.Resampling.BOX)
        if photo:
            btn = tk.Label(self.ctrl, image=photo, bg=BG, cursor="hand2", bd=0, highlightthickness=0)
            btn.image = photo
            btn.place(x=QUIT_BTN_X, y=QUIT_BTN_Y)
            btn.bind("<Button-1>", lambda e: self._quit())
            self.wgts.append(btn)
        
        lbl = tk.Label(self.ctrl, text="Team Builder", font=TITLE_FONT, fg=TXT, bg=BG)
        lbl.place(x=WINDOW_WIDTH // 2, y=TEAM_TITLE_Y, anchor="center")
        self.wgts.append(lbl)
        
        for i in range(6):
            self._build_card(i)
        
        self._build_btns()
    
    def _build_card(self, idx):
        col = idx % TEAM_CARD_COLS
        row = idx // TEAM_CARD_COLS
        x = TEAM_START_X + col * TEAM_SPACING_X
        y = TEAM_START_Y + row * TEAM_SPACING_Y
        
        card = tk.Frame(self.ctrl, bg=CARD_BG, width=TEAM_CARD_WIDTH, height=TEAM_CARD_HEIGHT,
                       highlightbackground=CARD_BG, highlightthickness=2)
        card.pack_propagate(False)
        card.place(x=x, y=y)
        self.wgts.append(card)
        
        x_btn = tk.Label(card, text="✕", font=TEAM_X_BTN_FONT, fg=MUTED_COLOR,
                        bg=CARD_BG, cursor="hand2")
        x_btn.place(x=TEAM_CARD_WIDTH - TEAM_X_BTN_OFFSET, y=TEAM_X_BTN_Y)
        x_btn.bind("<Button-1>", lambda e, i=idx: self._remove_poke(i))
        x_btn.bind("<Enter>", lambda e: x_btn.configure(fg=ACCENT_COLOR))
        x_btn.bind("<Leave>", lambda e: x_btn.configure(fg=MUTED_COLOR))
        x_btn.place_forget()
        
        egg = self._load_img(EGG_IMG, TEAM_EGG_SIZE)
        spr_lbl = tk.Label(card, bg=CARD_BG)
        if egg:
            spr_lbl.configure(image=egg)
            spr_lbl.image = egg
        spr_lbl.pack(pady=(20, 10))
        
        name_lbl = tk.Label(card, text="Select Pokémon", font=TEAM_NAME_FONT, 
                           fg=MUTED_COLOR, bg=CARD_BG)
        name_lbl.pack(pady=(0, 5))
        
        dd_btn = tk.Label(card, text="Pick ▼", font=TEAM_DD_BTN_FONT, fg=TXT,
                         bg=INPUT_BG_COLOR, cursor="hand2", padx=10, pady=5)
        dd_btn.pack(pady=(5, 0))
        dd_btn.bind("<Button-1>", lambda e, i=idx: self._toggle_dd(i))
        
        self.cards.append({
            'frame': card,
            'x_btn': x_btn,
            'sprite': spr_lbl,
            'name': name_lbl,
            'dd_btn': dd_btn,
            'x': x,
            'y': y
        })
    
    def _build_btns(self):
        rand_btn = tk.Label(self.ctrl, text="🎲 Randomise", font=NAV_FONT, fg=HIGHLIGHT_COLOR,
                           bg=ACCENT_COLOR, cursor="hand2", padx=20, pady=10)
        rand_btn.place(x=TEAM_RANDOM_BTN_X, y=TEAM_BTN_Y)
        rand_btn.bind("<Button-1>", lambda e: self._randomise())
        self.wgts.append(rand_btn)
        
        ana_btn = tk.Label(self.ctrl, text="📊 Analytics", font=NAV_FONT, fg=HIGHLIGHT_COLOR,
                          bg=ACCENT_COLOR, cursor="hand2", padx=20, pady=10)
        ana_btn.place(x=TEAM_ANALYTICS_BTN_X, y=TEAM_BTN_Y)
        ana_btn.bind("<Button-1>", lambda e: self._show_ana())
        self.wgts.append(ana_btn)
    
    # ==================== DROPDOWN ====================
    
    def _toggle_dd(self, idx):
        if self.dd_open == idx:
            self._close_dd()
        else:
            self._close_dd()
            self._open_dd(idx)
    
    def _open_dd(self, idx):
        if not self.all_pokes:
            self.wgts.append(self.err.show(ERR_NO_INTERNET, self._load_poke_list))
            return
        
        self.dd_open = idx
        self.dd_idx = idx
        card = self.cards[idx]
        
        x = card['x']
        y = card['y'] + TEAM_CARD_HEIGHT - 10
        
        dd = tk.Frame(self.ctrl, bg=CARD_BG, width=TEAM_DROPDOWN_WIDTH,
                     height=TEAM_DROPDOWN_HEIGHT, highlightbackground=HIGHLIGHT_COLOR,
                     highlightthickness=2)
        dd.place(x=x + 5, y=y)
        dd.pack_propagate(False)
        self.dd_wgts.append(dd)
        
        srch_var = tk.StringVar()
        srch_ent = tk.Entry(dd, textvariable=srch_var, font=TEAM_SEARCH_FONT,
                           bg=INPUT_BG_COLOR, fg=TXT, insertbackground=TXT, relief=tk.FLAT)
        srch_ent.pack(fill="x", padx=5, pady=5, ipady=3)
        srch_ent.insert(0, "Search...")
        srch_ent.bind("<FocusIn>", lambda e: self._on_srch_focus(srch_ent))
        srch_var.trace("w", lambda *args: self._filter_dd(srch_var.get()))
        
        cont = tk.Frame(dd, bg=CARD_BG)
        cont.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        cvs = tk.Canvas(cont, bg=INPUT_BG_COLOR, highlightthickness=0)
        scroll = tk.Scrollbar(cont, orient="vertical", command=cvs.yview)
        
        self.poke_list_fr = tk.Frame(cvs, bg=INPUT_BG_COLOR)
        cvs.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side=tk.RIGHT, fill="y")
        cvs.pack(side=tk.LEFT, fill="both", expand=True)
        cvs.create_window((0, 0), window=self.poke_list_fr, anchor="nw")
        
        self.dd_cvs = cvs
        self._populate_poke_list()
        
        self.poke_list_fr.update_idletasks()
        cvs.configure(scrollregion=cvs.bbox("all"))
        
        def on_wheel(e):
            cvs.yview_scroll(int(-1*(e.delta/120)), "units")
        
        cvs.bind("<Enter>", lambda e: cvs.bind_all("<MouseWheel>", on_wheel))
        cvs.bind("<Leave>", lambda e: cvs.unbind_all("<MouseWheel>"))
    
    def _on_srch_focus(self, ent):
        if ent.get() == "Search...":
            ent.delete(0, tk.END)
    
    def _populate_poke_list(self):
        if not self.poke_list_fr:
            return
        
        for w in self.poke_list_fr.winfo_children():
            w.destroy()
        
        for poke in self.filt_pokes[:TEAM_DD_LIMIT]:
            self._add_poke_row(poke)
        
        self.poke_list_fr.update_idletasks()
        if self.dd_cvs:
            self.dd_cvs.configure(scrollregion=self.dd_cvs.bbox("all"))
    
    def _add_poke_row(self, poke):
        row = tk.Frame(self.poke_list_fr, bg=INPUT_BG_COLOR, cursor="hand2")
        row.pack(fill="x", pady=1)
        
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{poke['id']}.png"
        spr = self._fetch(url, TEAM_MINI_SPRITE_SIZE, fallback=True)
        
        spr_lbl = None
        if spr:
            spr_lbl = tk.Label(row, image=spr, bg=INPUT_BG_COLOR)
            spr_lbl.image = spr
            spr_lbl.pack(side=tk.LEFT, padx=(5, 5))
        
        name_lbl = tk.Label(row, text=poke['name'].capitalize(), font=TEAM_ROW_FONT,
                           fg=TXT, bg=INPUT_BG_COLOR, anchor="w")
        name_lbl.pack(side=tk.LEFT, fill="x", expand=True)
        
        def enter(e):
            row.configure(bg=ACCENT_COLOR)
            name_lbl.configure(bg=ACCENT_COLOR)
            if spr_lbl:
                spr_lbl.configure(bg=ACCENT_COLOR)
        
        def leave(e):
            row.configure(bg=INPUT_BG_COLOR)
            name_lbl.configure(bg=INPUT_BG_COLOR)
            if spr_lbl:
                spr_lbl.configure(bg=INPUT_BG_COLOR)
        
        def click(e):
            self._select_poke(self.dd_idx, poke)
        
        wgts = [row, name_lbl]
        if spr_lbl:
            wgts.append(spr_lbl)
        
        for w in wgts:
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)
    
    def _filter_dd(self, query):
        if query and query != "Search...":
            q = query.lower()
            self.filt_pokes = [p for p in self.all_pokes if q in p['name'].lower()]
        else:
            self.filt_pokes = self.all_pokes.copy()
        self._populate_poke_list()
    
    def _close_dd(self):
        self._destroy(self.dd_wgts)
        self.dd_wgts = []
        self.dd_open = None
        self.dd_cvs = None
        self.dd_idx = None
        self.poke_list_fr = None
        self.filt_pokes = self.all_pokes.copy() if self.all_pokes else []
    
    # ==================== TEAM MANAGEMENT ====================
    
    def _select_poke(self, idx, poke_data):
        try:
            poke = get_pokemon(poke_data['id'])
            self.team[idx] = poke
            self._update_card(idx)
            self._close_dd()
        except NetworkError as e:
            self._close_dd()
            self.wgts.append(self.err.show(str(e), lambda: self._select_poke(idx, poke_data)))
        except PokeAPIError as e:
            self._close_dd()
            self.wgts.append(self.err.show(str(e)))
    
    def _remove_poke(self, idx):
        self.team[idx] = None
        self._update_card(idx)
    
    def _update_card(self, idx):
        card = self.cards[idx]
        poke = self.team[idx]
        
        if poke:
            spr = self._fetch(poke['sprite_url'], TEAM_SPRITE_SIZE, fallback=True)
            if spr:
                card['sprite'].configure(image=spr)
                card['sprite'].image = spr
            
            card['name'].configure(text=poke['name'], fg=TXT)
            card['dd_btn'].configure(text="Change ▼")
            card['x_btn'].place(x=TEAM_CARD_WIDTH - TEAM_X_BTN_OFFSET, y=TEAM_X_BTN_Y)
        else:
            egg = self._load_img(EGG_IMG, TEAM_EGG_SIZE)
            if egg:
                card['sprite'].configure(image=egg)
                card['sprite'].image = egg
            card['name'].configure(text="Select Pokémon", fg=MUTED_COLOR)
            card['dd_btn'].configure(text="Pick ▼")
            card['x_btn'].place_forget()
    
    def _randomise(self):
        self._close_dd()
        
        if not self.all_pokes:
            self.wgts.append(self.err.show(ERR_NO_INTERNET, self._load_poke_list))
            return
        
        picks = random.sample(self.all_pokes, min(6, len(self.all_pokes)))
        
        for i, poke_data in enumerate(picks):
            try:
                poke = get_pokemon(poke_data['id'])
                self.team[i] = poke
                self._update_card(i)
            except NetworkError as e:
                self.wgts.append(self.err.show(str(e)))
                return
            except PokeAPIError:
                pass
    
    # ==================== ANALYTICS ====================

    def _show_ana(self):
        self._close_dd()
        
        team_pokes = [p for p in self.team if p]
        if not team_pokes:
            self._show_empty_warn()
            return
        
        self._close_ana()
        
        popup = tk.Frame(self.ctrl, bg=CARD_BG, width=ANALYTICS_WIDTH, height=ANALYTICS_HEIGHT,
                        highlightbackground=GOLD_COLOR, highlightthickness=3)
        popup.place(x=ANALYTICS_X, y=ANALYTICS_Y)
        popup.pack_propagate(False)
        self.ana_popup = popup
        self.wgts.append(popup)
        
        title_fr = tk.Frame(popup, bg=CARD_BG)
        title_fr.pack(fill="x", padx=15, pady=(15, 10))
        
        tk.Label(title_fr, text="📊 Team Analytics", font=TITLE_FONT, fg=GOLD_COLOR, bg=CARD_BG
                ).pack(side=tk.LEFT)
        
        close_btn = tk.Label(title_fr, text="✕", font=TEAM_CLOSE_FONT, fg=MUTED_COLOR,
                            bg=CARD_BG, cursor="hand2")
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self._close_ana())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=ACCENT_COLOR))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=MUTED_COLOR))
        
        cont = tk.Frame(popup, bg=CARD_BG)
        cont.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        left = tk.Frame(cont, bg=CARD_BG)
        left.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        right = tk.Frame(cont, bg=CARD_BG)
        right.pack(side=tk.RIGHT, fill="both", expand=True, padx=(10, 0))
        
        self._build_weak(left, team_pokes)
        self._build_resist(left, team_pokes)
        self._build_stats(right, team_pokes)

    def _build_sec_fr(self, parent, title, emoji, color):
        fr = tk.Frame(parent, bg=ANALYTICS_SECTION_BG, highlightbackground=color,
                     highlightthickness=2)
        fr.pack(fill="x", pady=(0, 10))
        
        hdr = tk.Frame(fr, bg=ANALYTICS_SECTION_BG)
        hdr.pack(fill="x", padx=10, pady=(10, 5))
        
        tk.Label(hdr, text=f"{emoji} {title}", font=SUBTITLE_FONT, fg=color,
                bg=ANALYTICS_SECTION_BG).pack(anchor="w")
        
        cont = tk.Frame(fr, bg=ANALYTICS_SECTION_BG)
        cont.pack(fill="x", padx=10, pady=(0, 10))
        
        return cont

    def _build_weak(self, parent, team):
        cont = self._build_sec_fr(parent, "Weaknesses", "⚠️", ACCENT_COLOR)
        
        weak_cnt = {}
        for poke in team:
            weaks = get_pokemon_weaknesses(poke.get('types', []))
            for w in weaks:
                weak_cnt[w] = weak_cnt.get(w, 0) + 1
        
        sorted_weak = sorted(weak_cnt.items(), key=lambda x: -x[1])
        
        if sorted_weak:
            icons_fr = tk.Frame(cont, bg=ANALYTICS_SECTION_BG)
            icons_fr.pack(anchor="w")
            
            for i, (type_name, cnt) in enumerate(sorted_weak[:8]):
                cell = tk.Frame(icons_fr, bg=ANALYTICS_SECTION_BG)
                cell.grid(row=i // 4, column=i % 4, padx=5, pady=5)
                
                icon = self._type_icon(type_name)
                if icon:
                    lbl = tk.Label(cell, image=icon, bg=ANALYTICS_SECTION_BG)
                    lbl.image = icon
                    lbl.pack()
                    
                    clr = ACCENT_COLOR if cnt >= 3 else (GOLD_COLOR if cnt >= 2 else MUTED_COLOR)
                    badge = tk.Label(cell, text=f"×{cnt}", font=TEAM_BADGE_FONT,
                                    fg=clr, bg=ANALYTICS_SECTION_BG)
                    badge.pack()
        else:
            tk.Label(cont, text="No major weaknesses! ✓", font=BODY_FONT,
                    fg=RESIST_COLOR, bg=ANALYTICS_SECTION_BG).pack(anchor="w")

    def _build_resist(self, parent, team):
        cont = self._build_sec_fr(parent, "Resistances", "🛡️", RESIST_COLOR)
        
        resist_cnt = {}
        for poke in team:
            types = poke.get('types', [])
            for t in types:
                try:
                    r = requests.get(f"{TYPE_ENDPOINT}/{t.lower()}", timeout=3)
                    data = r.json()
                    for res in data['damage_relations']['half_damage_from']:
                        n = res['name'].capitalize()
                        resist_cnt[n] = resist_cnt.get(n, 0) + 1
                    for imm in data['damage_relations']['no_damage_from']:
                        n = imm['name'].capitalize()
                        resist_cnt[n] = resist_cnt.get(n, 0) + 2
                except:
                    pass
        
        sorted_resist = sorted(resist_cnt.items(), key=lambda x: -x[1])
        
        if sorted_resist:
            icons_fr = tk.Frame(cont, bg=ANALYTICS_SECTION_BG)
            icons_fr.pack(anchor="w")
            
            for i, (type_name, cnt) in enumerate(sorted_resist[:8]):
                cell = tk.Frame(icons_fr, bg=ANALYTICS_SECTION_BG)
                cell.grid(row=i // 4, column=i % 4, padx=5, pady=5)
                
                icon = self._type_icon(type_name)
                if icon:
                    lbl = tk.Label(cell, image=icon, bg=ANALYTICS_SECTION_BG)
                    lbl.image = icon
                    lbl.pack()
                    
                    clr = RESIST_COLOR if cnt >= 3 else (GOLD_COLOR if cnt >= 2 else MUTED_COLOR)
                    badge = tk.Label(cell, text=f"×{cnt}", font=TEAM_BADGE_FONT,
                                    fg=clr, bg=ANALYTICS_SECTION_BG)
                    badge.pack()
        else:
            tk.Label(cont, text="No resistances", font=BODY_FONT,
                    fg=MUTED_COLOR, bg=ANALYTICS_SECTION_BG).pack(anchor="w")

    def _build_stats(self, parent, team):
        cont = self._build_sec_fr(parent, "Team Stats", "📈", GOLD_COLOR)
        
        stats = {'hp': 0, 'attack': 0, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
        for poke in team:
            poke_stats = poke.get('stats', {})
            for s in stats:
                stats[s] += poke_stats.get(s, 0)
        
        cnt = len(team)
        for s in stats:
            stats[s] = int(stats[s] / cnt)
        
        stat_labels = {'hp': 'HP', 'attack': 'ATK', 'defense': 'DEF', 
                      'sp_attack': 'SpA', 'sp_defense': 'SpD', 'speed': 'SPD'}
        
        self.stat_bars = []
        
        for key in stats:
            row = tk.Frame(cont, bg=ANALYTICS_SECTION_BG)
            row.pack(fill="x", pady=4)
            
            clr = STAT_COLORS[key]
            
            tk.Label(row, text=stat_labels[key], font=TEAM_STAT_FONT, fg=TXT,
                    bg=ANALYTICS_SECTION_BG, width=4, anchor="w").pack(side=tk.LEFT)
            
            bar_bg = tk.Frame(row, bg=INPUT_BG_COLOR, width=STAT_BAR_WIDTH, height=STAT_BAR_HEIGHT)
            bar_bg.pack(side=tk.LEFT, padx=(10, 10))
            bar_bg.pack_propagate(False)
            
            bar_fill = tk.Frame(bar_bg, bg=clr, width=0, height=STAT_BAR_HEIGHT)
            bar_fill.place(x=0, y=0)
            
            tgt = int((stats[key] / ANALYTICS_MAX_STAT) * STAT_BAR_WIDTH)
            tgt = min(tgt, STAT_BAR_WIDTH)
            
            val_lbl = tk.Label(row, text=str(stats[key]), font=TEAM_STAT_FONT,
                              fg=clr, bg=ANALYTICS_SECTION_BG, width=4)
            val_lbl.pack(side=tk.LEFT)
            
            self.stat_bars.append({'bar': bar_fill, 'tgt': tgt, 'cur': 0})
        
        self._anim_bars()

    def _anim_bars(self):
        if not self.stat_bars:
            return
        
        done = True
        
        for b in self.stat_bars:
            if b['cur'] < b['tgt']:
                b['cur'] += 3
                if b['cur'] > b['tgt']:
                    b['cur'] = b['tgt']
                b['bar'].configure(width=b['cur'])
                done = False
        
        if not done and self.ana_popup:
            self.ana_popup.after(STAT_BAR_ANIM_SPEED, self._anim_bars)

    def _show_empty_warn(self):
        self._close_ana()
        
        popup = tk.Frame(self.ctrl, bg=CARD_BG, width=EMPTY_WARN_WIDTH, height=EMPTY_WARN_HEIGHT,
                        highlightbackground=ACCENT_COLOR, highlightthickness=3)
        popup.place(x=EMPTY_WARN_X, y=EMPTY_WARN_Y)
        popup.pack_propagate(False)
        self.ana_popup = popup
        self.wgts.append(popup)
        
        tk.Label(popup, text="⚠️ Add Pokémon first!", font=SUBTITLE_FONT,
                fg=ACCENT_COLOR, bg=CARD_BG).place(relx=0.5, rely=0.35, anchor="center")
        
        tk.Label(popup, text="Your team is empty", font=BODY_FONT,
                fg=MUTED_COLOR, bg=CARD_BG).place(relx=0.5, rely=0.55, anchor="center")
        
        ok_btn = tk.Label(popup, text="Got it", font=TEAM_OK_BTN_FONT, fg=HIGHLIGHT_COLOR,
                         bg=ACCENT_COLOR, cursor="hand2", padx=20, pady=8)
        ok_btn.place(relx=0.5, rely=0.8, anchor="center")
        ok_btn.bind("<Button-1>", lambda e: self._close_ana())

    def _close_ana(self):
        self.stat_bars = []
        
        if self.ana_popup:
            try:
                self.ana_popup.destroy()
                if self.ana_popup in self.wgts:
                    self.wgts.remove(self.ana_popup)
            except:
                pass
            self.ana_popup = None
    
    # ==================== NAVIGATION ====================
    
    def _quit(self):
        self._close_dd()
        self._close_ana()
        self.err.close()
        self._reset()
        self.ctrl.show("AppMenuFrame")