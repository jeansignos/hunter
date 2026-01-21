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
    
    # Garantir que o diretório existe
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f"[CACHE] Diretório criado: {CACHE_DIR}")
    
    cache_entry = {
        "timestamp": datetime.now().isoformat(),
        "expiry_minutes": expiry_minutes,
        "data": data
    }
    try:
        # Usar arquivo temporário para evitar corrupção
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', dir=CACHE_DIR, delete=False, encoding='utf-8') as tmp:
            json.dump(cache_entry, tmp, ensure_ascii=False)
            temp_path = tmp.name
        
        # Mover arquivo temporário para o destino final
        import shutil
        shutil.move(temp_path, cache_path)
        
        data_count = len(data) if isinstance(data, list) else 1
        print(f"[CACHE] Salvo com sucesso: {key} ({data_count} itens)")
        return True
    except Exception as e:
        print(f"[CACHE] Erro ao salvar cache {key}: {e}")
        import traceback
        traceback.print_exc()
        return False

def read_from_cache(key):
    """Lê dados do cache"""
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    
    if not os.path.exists(cache_path):
        print(f"[CACHE] Arquivo não existe: {cache_path}")
        return None
    
    try:
        file_size = os.path.getsize(cache_path)
        print(f"[CACHE] Lendo {key} ({file_size} bytes)...")
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_entry = json.load(f)
        
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        expiry_minutes = cache_entry.get("expiry_minutes", CACHE_EXPIRY_MINUTES)
        
        age_minutes = (datetime.now() - cache_time).total_seconds() / 60
        
        if datetime.now() - cache_time > timedelta(minutes=expiry_minutes):
            print(f"[CACHE] Cache {key} expirado (idade: {age_minutes:.1f}min, expira: {expiry_minutes}min)")
            return None
        
        data = cache_entry["data"]
        data_count = len(data) if isinstance(data, list) else 1
        print(f"[CACHE] Lido com sucesso: {key} ({data_count} itens, idade: {age_minutes:.1f}min)")
        return data
    except json.JSONDecodeError as e:
        print(f"[CACHE] Arquivo corrompido {key}: {e}")
        print(f"[CACHE] Deletando cache corrompido: {cache_path}")
        try:
            os.remove(cache_path)
            print(f"[CACHE] Cache {key} deletado com sucesso")
        except Exception as del_err:
            print(f"[CACHE] Erro ao deletar cache: {del_err}")
        return None
    except Exception as e:
        print(f"[CACHE] Erro ao ler cache {key}: {e}")
        import traceback
        traceback.print_exc()
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
