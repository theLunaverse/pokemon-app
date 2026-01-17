"""
Project Rotom - PokéAPI Module
Handles all API calls to PokéAPI with caching
"""

import requests
from modules.constants import *


# ==================== CUSTOM EXCEPTIONS ====================
class PokeAPIError(Exception):
    """Base exception for API errors"""
    pass

class NetworkError(PokeAPIError):
    """Raised when network connection fails"""
    pass

class PokemonNotFoundError(PokeAPIError):
    """Raised when pokemon is not found"""
    pass

class DataError(PokeAPIError):
    """Raised when data parsing fails"""
    pass


# ==================== CACHES ====================
_poke_cache = {}
_type_cache = {}
_names_cache = None
_species_cache = {}
_evo_cache = {}


# ==================== CORE ====================

def get_pokemon(id_or_name):
    """Get Pokemon data by name or ID"""
    key = str(id_or_name).lower()
    
    if key in _poke_cache:
        return _poke_cache[key]
    
    try:
        r = requests.get(f"{POKEMON_ENDPOINT}/{key}", timeout=10)
        
        if r.status_code == 404:
            raise PokemonNotFoundError(f"Pokemon '{id_or_name}' not found")
        
        r.raise_for_status()
        d = r.json()
        
        poke = {
            'name': d['name'].capitalize(),
            'id': d['id'],
            'sprite_url': d['sprites']['front_default'],
            'sprite_shiny_url': d['sprites']['front_shiny'],
            'height': d['height'],
            'weight': d['weight'],
            'types': [t['type']['name'].capitalize() for t in d['types']],
            'stats': {
                'hp': d['stats'][0]['base_stat'],
                'attack': d['stats'][1]['base_stat'],
                'defense': d['stats'][2]['base_stat'],
                'sp_attack': d['stats'][3]['base_stat'],
                'sp_defense': d['stats'][4]['base_stat'],
                'speed': d['stats'][5]['base_stat'],
            },
            'abilities': [a['ability']['name'].capitalize() for a in d['abilities']],
        }
        
        _poke_cache[key] = poke
        _poke_cache[str(poke['id'])] = poke
        return poke
    
    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException as e:
        raise NetworkError(ERR_LOAD_FAILED)
    except (KeyError, IndexError) as e:
        raise DataError(ERR_LOAD_FAILED)


def get_pokemon_by_type(type_name):
    """Get list of Pokemon IDs for a type"""
    key = type_name.lower()
    
    if key in _type_cache:
        return _type_cache[key]
    
    try:
        r = requests.get(f"{TYPE_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()
        
        pokes = []
        for entry in d['pokemon']:
            url = entry['pokemon']['url']
            pid = int(url.rstrip('/').split('/')[-1])
            pokes.append({'id': pid})
        
        _type_cache[key] = pokes
        return pokes
    
    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException:
        raise NetworkError(ERR_LOAD_FAILED)
    except (KeyError, ValueError):
        raise DataError(ERR_LOAD_FAILED)


def get_all_pokemon_names():
    """Get list of all pokemon names and IDs (fast, cached)"""
    global _names_cache
    
    if _names_cache is not None:
        return _names_cache
    
    try:
        r = requests.get(f"{POKEMON_ENDPOINT}?limit={TOTAL_POKEMON}", timeout=15)
        r.raise_for_status()
        d = r.json()
        
        _names_cache = [{'name': e['name'], 'id': i + 1} for i, e in enumerate(d['results'])]
        return _names_cache
    
    except requests.exceptions.ConnectionError:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.Timeout:
        raise NetworkError(ERR_NO_INTERNET)
    except requests.exceptions.RequestException:
        raise NetworkError(ERR_LOAD_FAILED)
    except KeyError:
        raise DataError(ERR_LOAD_FAILED)


def search_pokemon_by_name(query):
    """Search pokemon by partial name match"""
    q = query.lower()
    names = get_all_pokemon_names()
    return [p['id'] for p in names if q in p['name'].lower()]


def get_type_icon_url(type_name):
    """Get sprite URL for a Pokemon type"""
    tid = TYPE_IDS.get(type_name.lower())
    return f"{TYPE_ICON_URL}/{tid}.png" if tid else None


# ==================== SPECIES & EVOLUTION ====================

def get_pokemon_description(id_or_name):
    """Get flavor text description for a Pokemon"""
    key = str(id_or_name).lower()
    
    if key in _species_cache:
        return _species_cache[key]
    
    try:
        r = requests.get(f"{SPECIES_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()
        
        desc = ""
        for entry in d['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                desc = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                desc = ' '.join(desc.split())
                break
        
        _species_cache[key] = desc
        return desc
    except:
        return ""


def get_pokemon_weaknesses(types):
    """Calculate weaknesses for a Pokemon based on its types"""
    mults = {}
    
    for t in types:
        try:
            r = requests.get(f"{TYPE_ENDPOINT}/{t.lower()}", timeout=10)
            r.raise_for_status()
            d = r.json()
            
            for x in d['damage_relations']['double_damage_from']:
                n = x['name'].capitalize()
                mults[n] = mults.get(n, 1) * 2
            
            for x in d['damage_relations']['half_damage_from']:
                n = x['name'].capitalize()
                mults[n] = mults.get(n, 1) * 0.5
            
            for x in d['damage_relations']['no_damage_from']:
                n = x['name'].capitalize()
                mults[n] = 0
        except:
            pass
    
    return sorted([t for t, m in mults.items() if m > 1])


def get_evolution_chain(id_or_name):
    """Get evolution chain for a Pokemon"""
    key = str(id_or_name).lower()
    
    if key in _evo_cache:
        return _evo_cache[key]
    
    try:
        r = requests.get(f"{SPECIES_ENDPOINT}/{key}", timeout=10)
        r.raise_for_status()
        d = r.json()
        
        r2 = requests.get(d['evolution_chain']['url'], timeout=10)
        r2.raise_for_status()
        chain = r2.json()
        
        evos = []
        _parse_evo(chain['chain'], evos)
        
        for evo in evos:
            _evo_cache[evo['name'].lower()] = evos
            _evo_cache[str(evo['id'])] = evos
        
        return evos
    except:
        return []


def _parse_evo(node, evos):
    """Recursively parse evolution chain"""
    try:
        name = node['species']['name']
        poke = get_pokemon(name)
        if poke:
            evos.append({
                'name': poke['name'],
                'id': poke['id'],
                'sprite_url': poke['sprite_url']
            })
        for next_node in node.get('evolves_to', []):
            _parse_evo(next_node, evos)
    except:
        pass


# ==================== UTILITY ====================

def clear_caches():
    """Clear all caches"""
    global _poke_cache, _type_cache, _names_cache, _species_cache, _evo_cache
    _poke_cache = {}
    _type_cache = {}
    _names_cache = None
    _species_cache = {}
    _evo_cache = {}