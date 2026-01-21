"""
Funções de carregamento de contas com threading
"""
import os
import json
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.api import buscar_todas_contas, buscar_detalhes_conta
from core.cache import (
    CACHE_DIR, CACHE_DIR_DETALHES, 
    save_to_cache, read_from_cache, limpar_cache_contas
)
from core.filters import hash_status
from core.constants import NOMES_BLOQUEADOS, STATUS_DISPONIVEIS

# Variáveis globais para controle de carregamento
contas_detalhadas_global = []
cache_carregando = False
progresso_carregamento = {"atual": 0, "total": 0, "percentual": 0}
ultimo_hash_contas = ""
lock = threading.Lock()

# Controle de auto-renovação
AUTO_RENOVACAO_INTERVALO = 3 * 60 * 60  # 3 horas em segundos
auto_renovacao_ativa = False
auto_renovacao_thread = None
ultima_renovacao = None


def get_contas():
    """Retorna as contas carregadas globalmente"""
    global contas_detalhadas_global
    return contas_detalhadas_global


def is_cache_carregando():
    """Retorna se o cache está sendo carregado"""
    global cache_carregando
    return cache_carregando


def get_progresso():
    """Retorna o progresso do carregamento"""
    global progresso_carregamento, cache_carregando
    return {
        **progresso_carregamento,
        "em_andamento": cache_carregando
    }


def set_carregamento_status(status):
    """Define o status de carregamento"""
    global cache_carregando
    cache_carregando = status


def carregar_detalhes_com_cache(conta):
    """Carrega detalhes de uma conta com cache"""
    seq = conta.get("seq")
    transport_id = conta.get("transportID")
    
    if not seq or not transport_id:
        return None
    
    # Verificar cache
    cache_key = f"detalhes_{seq}_equip"
    cached = read_from_cache(cache_key)
    
    # Verificar se o cache tem os campos necessários
    # tradeType, nftID: necessários para filtro "Com Lance"
    # inven_all: precisa ter TODOS os itens com campo "trade" para busca funcionar
    # spirit: precisa ter contagem de espíritos lendários
    cache_valido = False
    if cached and "tradeType" in cached and "nftID" in cached:
        inven_all = cached.get("inven_all", [])
        spirit = cached.get("spirit", {})
        # Verifica se inven_all tem a nova estrutura com campo "trade"
        # e se tem mais itens que apenas os comercializáveis
        # e se spirit tem a estrutura correta
        if inven_all and len(inven_all) > 0 and isinstance(inven_all[0], dict) and "trade" in inven_all[0]:
            # Verificar se spirit existe e é um dict (não apenas default vazio)
            if isinstance(spirit, dict) and "lendarios" in spirit:
                cache_valido = True
    
    if cache_valido:
        return {
            "conta": conta,
            "detalhes": cached
        }
    
    # Buscar detalhes da API (cache inexistente ou incompleto)
    detalhes = buscar_detalhes_conta(seq, transport_id)
    
    if detalhes:
        # Salvar no cache para próximas consultas
        save_to_cache(cache_key, detalhes, expiry_minutes=720)
        return {
            "conta": conta,
            "detalhes": detalhes
        }
    
    return None


def carregar_contas_teste():
    """
    Carrega contas apenas da primeira página (para teste rápido).
    Ideal para desenvolvimento e debugging.
    """
    global contas_detalhadas_global, cache_carregando, progresso_carregamento
    
    if cache_carregando:
        print("[AVISO] Carregamento já em andamento")
        return
    
    cache_carregando = True
    print("[TESTE] Iniciando carregamento de teste (primeira página)")
    
    try:
        from core.api import buscar_lista_contas
        
        data = buscar_lista_contas(1)
        if not data:
            print("[ERRO] Falha ao buscar primeira página")
            cache_carregando = False
            return
        
        contas = data.get("data", {}).get("lists", [])
        
        # Filtrar contas bloqueadas
        contas = [c for c in contas if c.get("characterName", "") not in NOMES_BLOQUEADOS]
        
        total = len(contas)
        progresso_carregamento = {"atual": 0, "total": total, "percentual": 0}
        
        print(f"[TESTE] Carregando detalhes de {total} contas...")
        
        resultados = []
        status_coletados = set()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(carregar_detalhes_com_cache, conta): conta for conta in contas}
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    resultado = future.result(timeout=30)
                    if resultado:
                        detalhes = resultado.get("detalhes", {})
                        
                        # Mesclar detalhes com dados da conta
                        conta_info = resultado.get("conta", {})
                        conta_completa = {
                            "seq": conta_info.get("seq"),
                            "name": detalhes.get("basic", {}).get("name", conta_info.get("characterName")),
                            "worldName": detalhes.get("basic", {}).get("worldName", ""),
                            "class": detalhes.get("classe", conta_info.get("class", "1")),
                            "level": detalhes.get("basic", {}).get("level", 0),
                            "powerScore": detalhes.get("basic", {}).get("powerScore", 0),
                            "price": detalhes.get("price", 0),
                            **detalhes
                        }
                        resultados.append(conta_completa)
                        
                        # Coletar status para cache
                        for stat in detalhes.get("stats", []):
                            if isinstance(stat, dict) and stat.get("statName"):
                                status_coletados.add(stat["statName"])
                                
                except Exception as e:
                    print(f"[ERRO] Erro ao carregar conta: {e}")
                
                progresso_carregamento["atual"] = i + 1
                progresso_carregamento["percentual"] = int((i + 1) / total * 100)
        
        with lock:
            contas_detalhadas_global = resultados
        
        # Salvar no cache
        save_to_cache("contas_teste", resultados, expiry_minutes=720)
        
        # Salvar status disponíveis
        status_lista = list(status_coletados)
        save_to_cache("status_disponiveis", status_lista, expiry_minutes=720)
        
        print(f"[TESTE] Carregamento concluído: {len(resultados)} contas")
        
    except Exception as e:
        print(f"[ERRO] Erro no carregamento de teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cache_carregando = False


def carregar_contas_completas(force=False):
    """
    Carrega TODAS as contas disponíveis.
    Usa threading para acelerar o processo.
    
    Args:
        force: Se True, força recarregamento mesmo se já houver contas em cache
    """
    global contas_detalhadas_global, cache_carregando, progresso_carregamento, ultimo_hash_contas
    
    if cache_carregando:
        print("[AVISO] Carregamento já em andamento")
        return
    
    cache_carregando = True
    print("[COMPLETO] Iniciando carregamento completo de contas...")
    
    try:
        # Buscar todas as contas
        contas = buscar_todas_contas()
        
        if not contas:
            print("[ERRO] Nenhuma conta encontrada")
            cache_carregando = False
            return
        
        # Verificar se houve mudança na lista de contas
        novo_hash = hash_status(str(contas))
        
        if not force and novo_hash == ultimo_hash_contas and len(contas_detalhadas_global) > 0:
            print("[CACHE] Lista de contas não mudou, usando cache existente")
            cache_carregando = False
            return
        
        # Limpar cache se forçado
        if force:
            print("[LIMPEZA] Forçando limpeza de cache...")
            limpar_cache_contas()
        
        total = len(contas)
        progresso_carregamento = {"atual": 0, "total": total, "percentual": 0}
        
        print(f"[COMPLETO] Carregando detalhes de {total} contas...")
        
        resultados = []
        status_coletados = set()
        lote_tamanho = 10
        
        for i in range(0, total, lote_tamanho):
            lote = contas[i:i + lote_tamanho]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(carregar_detalhes_com_cache, conta): conta for conta in lote}
                
                for future in as_completed(futures):
                    try:
                        resultado = future.result(timeout=30)
                        if resultado:
                            detalhes = resultado.get("detalhes", {})
                            conta_info = resultado.get("conta", {})
                            
                            # Mesclar detalhes com dados da conta
                            conta_completa = {
                                "seq": conta_info.get("seq"),
                                "name": detalhes.get("basic", {}).get("name", conta_info.get("characterName")),
                                "worldName": detalhes.get("basic", {}).get("worldName", ""),
                                "class": detalhes.get("classe", conta_info.get("class", "1")),
                                "level": detalhes.get("basic", {}).get("level", 0),
                                "powerScore": detalhes.get("basic", {}).get("powerScore", 0),
                                "price": detalhes.get("price", 0),
                                **detalhes
                            }
                            resultados.append(conta_completa)
                            
                            # Coletar status
                            for stat in detalhes.get("stats", []):
                                if isinstance(stat, dict) and stat.get("statName"):
                                    status_coletados.add(stat["statName"])
                                    
                    except Exception as e:
                        print(f"[ERRO] Erro ao carregar conta: {e}")
            
            progresso_carregamento["atual"] = min(i + lote_tamanho, total)
            progresso_carregamento["percentual"] = int(progresso_carregamento["atual"] / total * 100)
            
            # Pequena pausa entre lotes
            if i + lote_tamanho < total:
                time.sleep(0.3)
        
        with lock:
            contas_detalhadas_global = resultados
            ultimo_hash_contas = novo_hash
        
        # Salvar no cache
        save_to_cache("contas_completas", resultados, expiry_minutes=720)
        
        # Salvar status disponíveis
        status_lista = list(status_coletados)
        save_to_cache("status_disponiveis", status_lista, expiry_minutes=720)
        
        # Salvar status do carregamento
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_contas": len(resultados),
            "hash": novo_hash
        }
        
        status_path = os.path.join(CACHE_DIR, "status_carregamento.json")
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        print(f"[COMPLETO] Carregamento concluído: {len(resultados)} contas")
        
    except Exception as e:
        print(f"[ERRO] Erro no carregamento completo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cache_carregando = False


def carregar_em_background():
    """Inicia carregamento em background usando thread"""
    thread = threading.Thread(target=carregar_contas_completas, daemon=True)
    thread.start()
    return thread


def carregar_teste_em_background():
    """Inicia carregamento de teste em background usando thread"""
    thread = threading.Thread(target=carregar_contas_teste, daemon=True)
    thread.start()
    return thread


def restaurar_do_cache():
    """
    Tenta restaurar contas do cache ao iniciar a aplicação.
    Retorna True se conseguiu restaurar, False caso contrário.
    """
    global contas_detalhadas_global, ultimo_hash_contas
    
    status_path = os.path.join(CACHE_DIR, "status_carregamento.json")
    
    if not os.path.exists(status_path):
        return False
    
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        # Verificar se o cache não é muito antigo (máximo 6 horas)
        timestamp = datetime.fromisoformat(status["timestamp"])
        if (datetime.now() - timestamp).total_seconds() > 21600:  # 6 horas
            print("[CACHE] Cache muito antigo (>6h), será recarregado")
            return False
        
        # Restaurar hash
        ultimo_hash_contas = status.get("hash", "")
        
        # Tentar restaurar contas dos arquivos de detalhes
        if os.path.exists(CACHE_DIR_DETALHES):
            contas_restauradas = []
            
            for filename in os.listdir(CACHE_DIR_DETALHES):
                if filename.startswith("detalhes_") and filename.endswith(".json"):
                    filepath = os.path.join(CACHE_DIR_DETALHES, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            cache_entry = json.load(f)
                        
                        detalhes = cache_entry.get("data")
                        if detalhes:
                            # Reconstruir entrada mínima de conta
                            seq = filename.replace("detalhes_", "").replace("_equip.json", "")
                            conta = {
                                "seq": seq,
                                "characterName": detalhes.get("basic", {}).get("name", ""),
                                "class": detalhes.get("classe", "1"),
                                "lv": detalhes.get("basic", {}).get("level", 0),
                                "powerScore": detalhes.get("basic", {}).get("powerScore", 0),
                                "price": detalhes.get("price", 0)
                            }
                            
                            contas_restauradas.append({
                                "conta": conta,
                                "detalhes": detalhes
                            })
                    except Exception as e:
                        print(f"[CACHE] Erro ao restaurar {filename}: {e}")
            
            if contas_restauradas:
                with lock:
                    contas_detalhadas_global = contas_restauradas
                print(f"[CACHE] Restauradas {len(contas_restauradas)} contas do cache")
                return True
        
    except Exception as e:
        print(f"[CACHE] Erro ao restaurar do cache: {e}")
    
    return False


# ========== SISTEMA DE AUTO-RENOVAÇÃO DO CACHE ==========

def renovar_cache_em_background():
    """
    Renova o cache carregando novos dados sem interromper o serviço.
    Os dados antigos continuam disponíveis até os novos estarem prontos.
    """
    global contas_detalhadas_global, cache_carregando, progresso_carregamento, ultimo_hash_contas, ultima_renovacao
    
    if cache_carregando:
        print("[AUTO-RENOVAÇÃO] Carregamento já em andamento, pulando...")
        return False
    
    print(f"[AUTO-RENOVAÇÃO] Iniciando renovação do cache... ({datetime.now().strftime('%H:%M:%S')})")
    
    # Guardar dados antigos em caso de erro
    dados_antigos = contas_detalhadas_global.copy() if contas_detalhadas_global else []
    
    cache_carregando = True
    
    try:
        # Buscar todas as contas
        contas = buscar_todas_contas()
        
        if not contas:
            print("[AUTO-RENOVAÇÃO] Nenhuma conta encontrada, mantendo cache antigo")
            cache_carregando = False
            return False
        
        total = len(contas)
        progresso_carregamento = {"atual": 0, "total": total, "percentual": 0}
        
        print(f"[AUTO-RENOVAÇÃO] Carregando detalhes de {total} contas...")
        
        resultados_novos = []
        status_coletados = set()
        lote_tamanho = 10
        
        for i in range(0, total, lote_tamanho):
            lote = contas[i:i + lote_tamanho]
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(carregar_detalhes_com_cache, conta): conta for conta in lote}
                
                for future in as_completed(futures):
                    try:
                        resultado = future.result(timeout=30)
                        if resultado:
                            detalhes = resultado.get("detalhes", {})
                            conta_info = resultado.get("conta", {})
                            
                            conta_completa = {
                                "seq": conta_info.get("seq"),
                                "name": detalhes.get("basic", {}).get("name", conta_info.get("characterName")),
                                "worldName": detalhes.get("basic", {}).get("worldName", ""),
                                "class": detalhes.get("classe", conta_info.get("class", "1")),
                                "level": detalhes.get("basic", {}).get("level", 0),
                                "powerScore": detalhes.get("basic", {}).get("powerScore", 0),
                                "price": detalhes.get("price", 0),
                                **detalhes
                            }
                            resultados_novos.append(conta_completa)
                            
                            for stat in detalhes.get("stats", []):
                                if isinstance(stat, dict) and stat.get("statName"):
                                    status_coletados.add(stat["statName"])
                                    
                    except Exception as e:
                        print(f"[AUTO-RENOVAÇÃO] Erro ao carregar conta: {e}")
            
            progresso_carregamento["atual"] = min(i + lote_tamanho, total)
            progresso_carregamento["percentual"] = int(progresso_carregamento["atual"] / total * 100)
            
            if i + lote_tamanho < total:
                time.sleep(0.3)
        
        # Verificar se conseguiu carregar dados
        if len(resultados_novos) == 0:
            print("[AUTO-RENOVAÇÃO] Nenhum resultado, mantendo cache antigo")
            cache_carregando = False
            return False
        
        # Só substituir se os novos dados são válidos
        if len(resultados_novos) >= len(dados_antigos) * 0.5:  # Pelo menos 50% dos dados antigos
            with lock:
                contas_detalhadas_global = resultados_novos
                novo_hash = hash_status(str(contas))
                ultimo_hash_contas = novo_hash
            
            # Salvar no cache
            save_to_cache("contas_completas", resultados_novos, expiry_minutes=720)
            
            status_lista = list(status_coletados)
            save_to_cache("status_disponiveis", status_lista, expiry_minutes=720)
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "total_contas": len(resultados_novos),
                "hash": novo_hash,
                "renovacao_automatica": True
            }
            
            status_path = os.path.join(CACHE_DIR, "status_carregamento.json")
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            
            ultima_renovacao = datetime.now()
            print(f"[AUTO-RENOVAÇÃO] Concluída com sucesso: {len(resultados_novos)} contas ({datetime.now().strftime('%H:%M:%S')})")
            return True
        else:
            print(f"[AUTO-RENOVAÇÃO] Poucos resultados ({len(resultados_novos)}), mantendo cache antigo ({len(dados_antigos)})")
            return False
        
    except Exception as e:
        print(f"[AUTO-RENOVAÇÃO] Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cache_carregando = False


def _loop_auto_renovacao():
    """Loop interno que verifica e renova o cache periodicamente"""
    global auto_renovacao_ativa, ultima_renovacao
    
    print(f"[AUTO-RENOVAÇÃO] Sistema iniciado - Intervalo: {AUTO_RENOVACAO_INTERVALO / 3600:.1f} horas")
    
    while auto_renovacao_ativa:
        try:
            # Verificar se precisa renovar
            agora = datetime.now()
            
            if ultima_renovacao is None:
                # Primeira execução, aguardar intervalo completo
                ultima_renovacao = agora
                print(f"[AUTO-RENOVAÇÃO] Próxima renovação em {AUTO_RENOVACAO_INTERVALO / 3600:.1f} horas")
            
            segundos_desde_ultima = (agora - ultima_renovacao).total_seconds()
            
            if segundos_desde_ultima >= AUTO_RENOVACAO_INTERVALO:
                print(f"[AUTO-RENOVAÇÃO] Intervalo atingido ({segundos_desde_ultima / 3600:.1f}h), iniciando renovação...")
                renovar_cache_em_background()
            
            # Dormir por 5 minutos antes de verificar novamente
            for _ in range(60):  # 60 x 5 segundos = 5 minutos
                if not auto_renovacao_ativa:
                    break
                time.sleep(5)
                
        except Exception as e:
            print(f"[AUTO-RENOVAÇÃO] Erro no loop: {e}")
            time.sleep(60)


def iniciar_auto_renovacao():
    """Inicia o sistema de auto-renovação em background"""
    global auto_renovacao_ativa, auto_renovacao_thread, ultima_renovacao
    
    if auto_renovacao_ativa:
        print("[AUTO-RENOVAÇÃO] Já está ativo")
        return False
    
    auto_renovacao_ativa = True
    ultima_renovacao = datetime.now()  # Considera que acabou de carregar
    
    auto_renovacao_thread = threading.Thread(target=_loop_auto_renovacao, daemon=True)
    auto_renovacao_thread.start()
    
    print("[AUTO-RENOVAÇÃO] Sistema de auto-renovação iniciado")
    return True


def parar_auto_renovacao():
    """Para o sistema de auto-renovação"""
    global auto_renovacao_ativa
    
    auto_renovacao_ativa = False
    print("[AUTO-RENOVAÇÃO] Sistema de auto-renovação parado")


def get_status_auto_renovacao():
    """Retorna o status do sistema de auto-renovação"""
    global auto_renovacao_ativa, ultima_renovacao, AUTO_RENOVACAO_INTERVALO
    
    proxima = None
    if ultima_renovacao:
        segundos_restantes = AUTO_RENOVACAO_INTERVALO - (datetime.now() - ultima_renovacao).total_seconds()
        if segundos_restantes > 0:
            horas = int(segundos_restantes // 3600)
            minutos = int((segundos_restantes % 3600) // 60)
            proxima = f"{horas}h {minutos}min"
    
    return {
        "ativo": auto_renovacao_ativa,
        "ultima_renovacao": ultima_renovacao.isoformat() if ultima_renovacao else None,
        "intervalo_horas": AUTO_RENOVACAO_INTERVALO / 3600,
        "proxima_em": proxima
    }
