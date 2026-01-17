from functools import lru_cache

import requests

from modules.constants import *


class PokeAPIError(Exception):
    pass


class NetworkError(PokeAPIError):
    pass


class PokemonNotFoundError(PokeAPIError):
    pass


class DataError(PokeAPIError):
    pass


@lru_cache()
def get_pokemon(id_or_name):
    key = str(id_or_name).lower().strip()

    try:
        r = requests.get(f"{POKEMON_ENDPOINT}/{key}", timeout=10)

        if r.status_code == 404:
            raise PokemonNotFoundError(f"Pokemon '{id_or_name}' not found")

        r.raise_for_status()
        d = r.json()

        return {
            "name": d["name"].capitalize(),
            "id": d["id"],
            "sprite_url": d["sprites"]["front_default"],
            "sprite_shiny_url": d["sprites"]["front_shiny"],
            "height": d["height"],
            "weight": d["weight"],
            "types": [t["type"]["name"].capitalize() for t in d["types"]],
            "stats": {
                "hp": d["stats"][0]["base_stat"],
                "attack": d["stats"][1]["base_stat"],
                "defense": d["stats"][2]["base_stat"],
                "sp_attack": d["stats"][3]["base_stat"],
                "sp_defense": d["stats"][4]["base_stat"],
                "speed": d["stats"][5]["base_stat"],
            },
            "abilities": [a["ability"]["name"].capitalize() for a in d["abilities"]],
        }

    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException:
        raise NetworkError(ERR_LOAD_FAILED)
    except (KeyError, IndexError):
        raise DataError(ERR_LOAD_FAILED)


@lru_cache()
def get_pokemon_by_type(type_name):
    key = str(type_name).lower()

    try:
        r = requests.get(f"{TYPE_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()

        pokes = []
        for entry in d["pokemon"]:
            url = entry["pokemon"]["url"]
            pid = int(url.rstrip("/").split("/")[-1])
            pokes.append({"id": pid})

        return pokes

    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException:
        raise NetworkError(ERR_LOAD_FAILED)
    except (KeyError, ValueError):
        raise DataError(ERR_LOAD_FAILED)


@lru_cache()
def get_all_pokemon_names():
    try:
        r = requests.get(f"{POKEMON_ENDPOINT}?limit={TOTAL_POKEMON}", timeout=15)
        r.raise_for_status()
        d = r.json()

        return [
            {"name": e["name"].lower(), "id": i + 1} for i, e in enumerate(d["results"])
        ]

    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException:
        raise NetworkError(ERR_LOAD_FAILED)
    except KeyError:
        raise DataError(ERR_LOAD_FAILED)


def search_pokemon_by_name(query):
    q = query.lower()
    names = get_all_pokemon_names()
    return [p["id"] for p in names if p["name"].startswith(q)]


@lru_cache()
def get_type_icon_url(type_name):
    tid = TYPE_IDS.get(type_name.lower())
    return f"{TYPE_ICON_URL}/{tid}.png" if tid else None


@lru_cache()
def get_pokemon_description(id_or_name):
    key = str(id_or_name).lower()
    try:
        r = requests.get(f"{SPECIES_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()

        for entry in d["flavor_text_entries"]:
            if entry["language"]["name"] == "en":
                desc = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                return " ".join(desc.split())
        return ""
    except:
        return ""


@lru_cache()
def _fetch_type_data(type_name):
    r = requests.get(f"{TYPE_ENDPOINT}/{type_name}", timeout=10)
    r.raise_for_status()
    return r.json()


def get_pokemon_weaknesses(types):
    mults = {}

    for t in types:
        try:
            d = _fetch_type_data(t.lower())

            for x in d["damage_relations"]["double_damage_from"]:
                n = x["name"].capitalize()
                mults[n] = mults.get(n, 1) * 2

            for x in d["damage_relations"]["half_damage_from"]:
                n = x["name"].capitalize()
                mults[n] = mults.get(n, 1) * 0.5

            for x in d["damage_relations"]["no_damage_from"]:
                n = x["name"].capitalize()
                mults[n] = 0
        except:
            pass

    return sorted([t for t, m in mults.items() if m > 1])


@lru_cache()
def get_evolution_chain(id_or_name):
    key = str(id_or_name).lower()
    try:
        r = requests.get(f"{SPECIES_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()

        r2 = requests.get(d["evolution_chain"]["url"], timeout=10)
        r2.raise_for_status()
        chain = r2.json()

        evos = []
        _parse_evo(chain["chain"], evos)

        return evos
    except:
        return []


def _parse_evo(node, evos):
    try:
        name = node["species"]["name"]
        poke = get_pokemon(name)
        if poke:
            evos.append(
                {
                    "name": poke["name"],
                    "id": poke["id"],
                    "sprite_url": poke["sprite_url"],
                }
            )
        for next_node in node.get("evolves_to", []):
            _parse_evo(next_node, evos)
    except:
        pass
