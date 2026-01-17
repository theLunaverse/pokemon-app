import os

# ==================== WINDOW DIMENSIONS ====================
WINDOW_WIDTH = 1090
WINDOW_HEIGHT = 670

# ==================== COLORS ====================
BG_COLOR = "#000000"
LABEL_BG_COLOR = "#464646"
CARD_BG_COLOR = "#2A2A2A"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FF5733"
HIGHLIGHT_COLOR = "#FFFFFF"
MUTED_COLOR = "#AAAAAA"
GOLD_COLOR = "#FFD700"
INPUT_BG_COLOR = "#3A3A3A"
HOVER_BG_COLOR = "#4A4A4A"

# ==================== FONTS ====================
FONT_NAME = "Courier"

TITLE_FONT = (FONT_NAME, -24, "bold")
SUBTITLE_FONT = (FONT_NAME, -18, "bold")
BODY_FONT = (FONT_NAME, -18)

POKE_NAME_FONT = (FONT_NAME, -18, "bold")
POKE_ID_FONT = (FONT_NAME, -14)
POKE_DETAIL_NAME_FONT = (FONT_NAME, -28, "bold")
POKE_DETAIL_ID_FONT = (FONT_NAME, -22)
SEARCH_BTN_FONT = (FONT_NAME, -12)
FILTER_FONT = (FONT_NAME, -11)
NAV_FONT = (FONT_NAME, -14)
SECTION_FONT = (FONT_NAME, -14, "bold")
EVO_NAME_FONT = (FONT_NAME, -12)
ARROW_FONT = (FONT_NAME, -18, "bold")
SHINY_BTN_FONT = (FONT_NAME, -14, "bold")
TEAM_X_BTN_FONT = (FONT_NAME, -12, "bold")
TEAM_NAME_FONT = (FONT_NAME, -12, "bold")
TEAM_DD_BTN_FONT = (FONT_NAME, -11)
TEAM_SEARCH_FONT = (FONT_NAME, -11)
TEAM_ROW_FONT = (FONT_NAME, -11)
TEAM_CLOSE_FONT = (FONT_NAME, -20, "bold")
TEAM_BADGE_FONT = (FONT_NAME, -14, "bold")
TEAM_STAT_FONT = (FONT_NAME, -14, "bold")
TEAM_OK_BTN_FONT = (FONT_NAME, -14)

# ==================== ASSET PATHS ====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_DIR, "assets")

START_SCREEN_BG = os.path.join(ASSETS_PATH, "start_screen.gif")
ROTOM_PHONE_BG = os.path.join(ASSETS_PATH, "rotom_phone.gif")
QUIT_BUTTON_IMG = os.path.join(ASSETS_PATH, "quit_btn.png")
BACK_BUTTON_IMG = os.path.join(ASSETS_PATH, "back_btn.png")
START_BUTTON_IMG = os.path.join(ASSETS_PATH, "start_btn.png")
POKEDEX_ICON = os.path.join(ASSETS_PATH, "pokedex_icon.png")
TEAM_BUILDER_ICON = os.path.join(ASSETS_PATH, "team_icon.png")
TUTORIAL_ICON = os.path.join(ASSETS_PATH, "tutorial_icon.png")

# ==================== START BUTTON ====================
START_BTN_X = 425
START_BTN_Y = 455
START_BTN_WIDTH = 200
START_BTN_HEIGHT = 80

# ==================== API CONFIGURATION ====================
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{POKEAPI_BASE_URL}/pokemon"
TYPE_ENDPOINT = f"{POKEAPI_BASE_URL}/type"

ANIMATED_SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated"
SHINY_ANIMATED_SPRITE_URL = f"{ANIMATED_SPRITE_URL}/shiny"

# ==================== HOW TO USE ====================
TUT_MENU_BG = os.path.join(ASSETS_PATH, "tut_menu.png")

POKE_TUT = [
    os.path.join(ASSETS_PATH, "poke_1.png"),
    os.path.join(ASSETS_PATH, "poke_2.png"),
    os.path.join(ASSETS_PATH, "poke_3.gif"),
    os.path.join(ASSETS_PATH, "poke_4.gif"),
    os.path.join(ASSETS_PATH, "poke_5.png"),
    os.path.join(ASSETS_PATH, "poke_6.png"),
    os.path.join(ASSETS_PATH, "poke_7.png"),
    os.path.join(ASSETS_PATH, "poke_8.png"),
    os.path.join(ASSETS_PATH, "poke_9.png"),
    os.path.join(ASSETS_PATH, "poke_10.png"),
]

TUT_ICON_SIZE = (120, 120)
TUT_START_X = 430
TUT_START_Y = 300
TUT_SPACING_X = 180
TUT_LABEL_OFFSET_X = 60
TUT_LABEL_OFFSET_Y = 145

TUT_LOC1_X = 873
TUT_LOC1_NEXT_Y = 540
TUT_LOC1_PREV_Y = 590

TUT_LOC2_X = 430
TUT_LOC2_NEXT_Y = 530
TUT_LOC2_PREV_Y = 580

TUT_LOC3_X = 420
TUT_LOC3_Y = 395
TUT_LOC3_SPACING = 150

TUT_BTN_FONT = (FONT_NAME, -14)
TUT_BTN_PAD_X = 20
TUT_BTN_PAD_Y = 8

POKE_TUT_CFG = [
    (1, False),
    (1, False),
    (1, True),
    (1, True),
    (2, False),
    (2, False),
    (1, False),
    (1, False),
    (1, False),
    (3, False),
]

TEAM_TUT = [
    os.path.join(ASSETS_PATH, "tb_1.png"),
    os.path.join(ASSETS_PATH, "tb_2.png"),
    os.path.join(ASSETS_PATH, "tb_3.png"),
    os.path.join(ASSETS_PATH, "tb_4.png"),
    os.path.join(ASSETS_PATH, "tb_5.png"),
    os.path.join(ASSETS_PATH, "tb_6.png"),
    os.path.join(ASSETS_PATH, "tb_7.png"),
]

TEAM_TUT_CFG = [
    (1, False),
    (1, False),
    (1, False),
    (2, False),
    (1, False),
    (2, False),
    (3, False),
]

# ==================== CARD DIMENSIONS ====================
CARD_WIDTH = 200
CARD_HEIGHT = 200
DETAIL_CARD_LEFT_WIDTH = 300
DETAIL_CARD_RIGHT_WIDTH = 400
DETAIL_CARD_HEIGHT = 340

# ==================== SPRITE SIZES ====================
CARD_SPRITE_SIZE = (100, 100)
CARD_ANIM_SIZE = (80, 80)
DETAIL_SPRITE_SIZE = (150, 150)
EVO_SPRITE_SIZE = (60, 60)
TYPE_ICON_SIZE = (85, 28)
BACK_BTN_SIZE = (120, 35)

# ==================== QUIT BUTTON ====================
QUIT_BTN_X = 150
QUIT_BTN_Y = 140
QUIT_BTN_WIDTH = 120
QUIT_BTN_HEIGHT = 35

# ==================== BACK BUTTON ====================
BACK_BTN_X = 780
BACK_BTN_Y = 140

# ==================== POKEMON DATA ====================
TOTAL_POKEMON = 1025
MAX_ANIMATED_ID = 649
CARDS_PER_PAGE = 3

# ==================== POKEMON TYPES ====================
POKEMON_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

# ==================== SEARCH BAR ====================
SEARCH_X = 290
SEARCH_Y = 135
SEARCH_WIDTH = 500
SEARCH_HEIGHT = 40

# ==================== TYPE FILTER ====================
FILTER_X = 185
FILTER_Y = 195
FILTER_WIDTH = 700
FILTER_HEIGHT = 50
TYPES_PER_ROW = 9

# ==================== CARD POSITIONS ====================
CARD_START_X = 230
CARD_START_Y = 260
CARD_SPACING_X = 230
CARD_SPACING_Y = 230

# ==================== DETAIL VIEW ====================
DETAIL_LEFT_X = 200
DETAIL_RIGHT_X = 520
DETAIL_Y = 185
SHINY_BTN_X = 260
SHINY_BTN_Y = 10
DESC_MAX_LEN = 150
WEAK_PER_ROW = 3

# ==================== NAV BUTTONS ====================
PREV_BTN_X = 420
NEXT_BTN_X = 620
NAV_BTN_Y = 480
PAGE_LBL_X = 500
PAGE_LBL_Y = 515

# ==================== TYPE DATA ====================
TYPE_IDS = {
    'normal': 1, 'fighting': 2, 'flying': 3, 'poison': 4,
    'ground': 5, 'rock': 6, 'bug': 7, 'ghost': 8,
    'steel': 9, 'fire': 10, 'water': 11, 'grass': 12,
    'electric': 13, 'psychic': 14, 'ice': 15, 'dragon': 16,
    'dark': 17, 'fairy': 18,
}

TYPE_ICON_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-viii/sword-shield"
SPECIES_ENDPOINT = f"{POKEAPI_BASE_URL}/pokemon-species"

# ==================== APP MENU ====================
MENU_ICON_SIZE = (165, 165)
MENU_START_X = 265
MENU_START_Y = 220
MENU_SPACING_X = 200
MENU_SPACING_Y = 200
MENU_LABEL_OFFSET_X = 75
MENU_LABEL_OFFSET_Y = 220

MENU_APPS = [
    {'name': 'How to Use', 'icon': TUTORIAL_ICON, 'frame': 'HowToUseFrame'},
    {'name': 'Pokédex', 'icon': POKEDEX_ICON, 'frame': 'PokedexFrame'},
    {'name': 'Team Builder', 'icon': TEAM_BUILDER_ICON, 'frame': 'TeamBuilderFrame'},
]

# ==================== TEAM BUILDER ====================
EGG_IMG = os.path.join(ASSETS_PATH, "egg.png")

TEAM_TITLE_Y = 150
TEAM_CARD_WIDTH = 180
TEAM_CARD_HEIGHT = 158
TEAM_CARD_COLS = 3
TEAM_START_X = 250
TEAM_START_Y = 180
TEAM_SPACING_X = 220
TEAM_SPACING_Y = 165

TEAM_EGG_SIZE = (72, 72)
TEAM_SPRITE_SIZE = (72, 72)
TEAM_MINI_SPRITE_SIZE = (27, 27)

TEAM_DROPDOWN_WIDTH = 126
TEAM_DROPDOWN_HEIGHT = 162
TEAM_DD_LIMIT = 50

TEAM_BTN_Y = 510
TEAM_RANDOM_BTN_X = 360
TEAM_ANALYTICS_BTN_X = 560

TEAM_X_BTN_OFFSET = 25
TEAM_X_BTN_Y = 5

# ==================== ANALYTICS ====================
ANALYTICS_WIDTH = 700
ANALYTICS_HEIGHT = 445
ANALYTICS_X = 220
ANALYTICS_Y = 110
ANALYTICS_SECTION_BG = "#363636"
STAT_BAR_WIDTH = 200
STAT_BAR_HEIGHT = 16
STAT_BAR_ANIM_SPEED = 10
ANALYTICS_MAX_STAT = 150

STAT_COLORS = {
    'hp': '#FF5959',
    'attack': '#F5AC78',
    'defense': '#FAE078',
    'sp_attack': '#9DB7F5',
    'sp_defense': '#A7DB8D',
    'speed': '#FA92B2'
}

RESIST_COLOR = "#4CAF50"

EMPTY_WARN_WIDTH = 350
EMPTY_WARN_HEIGHT = 120
EMPTY_WARN_X = 370
EMPTY_WARN_Y = 280

# ==================== ERROR HANDLING ====================
ERROR_IMG = os.path.join(ASSETS_PATH, "error.png")
ERROR_IMG_SIZE = (80, 80)
ERROR_POPUP_WIDTH = 450
ERROR_POPUP_HEIGHT = 180
ERROR_POPUP_X = 320
ERROR_POPUP_Y = 245

ERR_NO_INTERNET = "Please connect to the internet\nto load Pokémon data"
ERR_LOAD_FAILED = "Failed to load data\nPlease try again"