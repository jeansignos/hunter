"""
Funções de cache do sistema
"""
import os
import json
import glob
import shutil
from datetime import datetime, timedelta

CACHE_DIR = "xdraco_cache_status"
CACHE_DIR_DETALHES = os.path.join(CACHE_DIR, "detalhes")
CACHE_EXPIRY_MINUTES = 720

# Criar diretórios de cache se não existirem
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
if not os.path.exists(CACHE_DIR_DETALHES):
    os.makedirs(CACHE_DIR_DETALHES)


def get_cache_key(*args):
    """Gera uma chave de cache a partir dos argumentos"""
    import hashlib
    key_string = "_".join(str(a) for a in args)
    return hashlib.md5(key_string.encode()).hexdigest()


def save_to_cache(key, data, expiry_minutes=CACHE_EXPIRY_MINUTES):
    """Salva dados no cache"""
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "expiry_minutes": expiry_minutes,
        "data": data
    }
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar cache {key}: {e}")
        return False


def read_from_cache(key):
    """Lê dados do cache"""
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_entry = json.load(f)
        
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        expiry_minutes = cache_entry.get("expiry_minutes", CACHE_EXPIRY_MINUTES)
        
        if datetime.now() - cache_time > timedelta(minutes=expiry_minutes):
            return None
        
        return cache_entry["data"]
    except Exception as e:
        print(f"Erro ao ler cache {key}: {e}")
        return None


def limpar_cache_contas():
    """Limpa apenas os arquivos de cache relacionados a contas"""
    try:
        # Arquivos principais de contas
        cache_files = ["contas_completas", "contas_teste", "status_disponiveis"]
        for cache_key in cache_files:
            cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
            if os.path.exists(cache_path):
                os.remove(cache_path)
                print(f"[CACHE] Arquivo {cache_key}.json removido")
        
        # Limpa cache de detalhes de contas
        detalhes_files = glob.glob(os.path.join(CACHE_DIR, "detalhes_*_equip.json"))
        for file_path in detalhes_files:
            os.remove(file_path)
            
        # Limpa cache de lista de contas
        lista_files = glob.glob(os.path.join(CACHE_DIR, "lista_contas_page_*.json"))
        for file_path in lista_files:
            os.remove(file_path)
            
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao limpar cache de contas: {e}")
        return False


def limpar_todo_cache():
    """Limpa todo o cache incluindo WEMIX"""
    try:
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
            os.makedirs(CACHE_DIR)
            print("[CACHE] Todo o cache foi limpo")
            return True
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao limpar todo o cache: {e}")
        return False
