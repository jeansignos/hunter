"""
Funções de API para buscar dados do xDraco
"""
import os
import json
import requests
from datetime import datetime, timedelta
from core.cache import CACHE_DIR, save_to_cache, read_from_cache
from core.constants import NOMES_BLOQUEADOS, CLASSE_PARA_PASTA

# Sessão HTTP compartilhada
session = requests.Session()


def get_wemix_brl_price():
    """Obtém preço do WEMIX em BRL da CoinMarketCap"""
    cache_key = "wemix_brl_price"
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            cache_time = datetime.fromisoformat(cache_entry["timestamp"])
            if datetime.now() - cache_time < timedelta(minutes=5):
                return cache_entry["data"]
        except Exception as e:
            print(f"[ERRO] Falha ao ler cache WEMIX: {e}")
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {'symbol': 'WEMIX', 'convert': 'BRL'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.environ.get('CMC_API_KEY', '051cc3b82a9446fa9771425ab96bd91b')
    }

    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        brl_price = data['data']['WEMIX']['quote']['BRL']['price']
        
        cache_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": brl_price
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        
        return brl_price
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar preço WEMIX: {e}")
    
    return None


def buscar_lista_contas(page=1):
    """Busca lista de contas da API do xDraco"""
    cache_key = f"lista_contas_page_{page}"
    cached = read_from_cache(cache_key)
    if cached:
        return cached
    
    url = f"https://webapi.mir4global.com/nft/lists?listType=sale&class=0&levMin=0&levMax=0&powerMin=0&powerMax=0&priceMin=0&priceMax=0&sort=latest&page={page}&languageCode=pt"
    
    try:
        response = session.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            save_to_cache(cache_key, data, expiry_minutes=30)
            return data
        else:
            print(f"Erro HTTP {response.status_code} na página {page}")
    except Exception as e:
        print(f"Erro ao buscar página {page}: {e}")
    
    return None


def buscar_todas_contas(max_paginas=100):
    """Busca contas disponíveis (limitado por max_paginas)"""
    import time
    
    print(f"Iniciando busca de contas (max {max_paginas} páginas)...")
    todas_contas = []
    pagina = 1
    
    while pagina <= max_paginas:
        print(f"Buscando página {pagina}...")
        data = buscar_lista_contas(pagina)
        
        if not data:
            print(f"Erro na página {pagina}, parando...")
            break
        
        data_dict = data.get("data", {})
        contas = data_dict.get("lists", [])
        
        if not contas:
            print(f"Página {pagina} vazia, fim das contas.")
            break
        
        # Filtrar contas bloqueadas
        contas_filtradas = [c for c in contas if c.get("characterName", "") not in NOMES_BLOQUEADOS]
        todas_contas.extend(contas_filtradas)
        
        total_count = data_dict.get("totalCount", 0)
        if len(todas_contas) >= total_count:
            print(f"Todas as {total_count} contas foram coletadas")
            break
        
        pagina += 1
        time.sleep(0.5)
    
    print(f"Total de contas coletadas: {len(todas_contas)}")
    return todas_contas


def buscar_equipamentos_equipados(seq):
    """Busca equipamentos equipados de uma conta"""
    url = f"https://webapi.mir4global.com/nft/character/summary?seq={seq}&languageCode=pt"
    equipamentos = []
    
    TIPO_POR_SLOT = {
        "2_1": "Arma", "2_2": "Arma", "2_3": "Arma", "2_4": "Arma", 
        "2_5": "Arma", "2_6": "Arma", "2_7": "Arma",
        "20_1": "Arma Secundária",
        "3_1": "Torso", "3_2": "Pernas", "3_3": "Luvas", "3_4": "Botas",
        "4_1": "Colar", "4_2": "Pulseira", "4_3": "Anel", "4_4": "Brincos"
    }
    
    try:
        res = session.get(url, timeout=10)
        if res.ok:
            data = res.json().get("data", {}).get("equipItem", {})
            if isinstance(data, dict):
                for slot_key, item in data.items():
                    if not isinstance(item, dict):
                        continue
                        
                    item_type = str(item.get("itemType", ""))
                    if item_type not in TIPO_POR_SLOT:
                        continue
                    
                    grade = int(item.get("grade", 0))
                    if grade not in [3, 4, 5]:
                        continue
                    
                    item_idx = str(item.get("itemIdx", ""))
                    is_trade = len(item_idx) >= 4 and item_idx[3] == "1"
                    
                    cor_fundo = ""
                    if grade == 5:
                        cor_fundo = "fundo-lendario"
                    elif grade == 4:
                        cor_fundo = "fundo-epico"
                    elif grade == 3:
                        cor_fundo = "fundo-raro"
                    
                    equipamentos.append({
                        "slot": TIPO_POR_SLOT[item_type],
                        "tipo": item_type,
                        "nome": item.get("itemName", "Desconhecido"),
                        "img": item.get("itemPath", ""),
                        "aprimoramento": int(item.get("enhance", 0)),
                        "tier": item.get("tier", "I"),
                        "grade": grade,
                        "trade": is_trade,
                        "cor_fundo": cor_fundo
                    })
    except Exception as e:
        print(f"Erro ao buscar equipamentos: {e}")
    
    return equipamentos


def buscar_spirit_detalhado(transport_id):
    """Busca espíritos detalhados"""
    # Usando languageCode=en para que os nomes batam com o filtro HTML (em inglês)
    url = f"https://webapi.mir4global.com/nft/character/spirit?transportID={transport_id}&languageCode=en"
    
    try:
        res = session.get(url, timeout=10)
        if res.ok:
            data = res.json().get("data", {})
            
            pets = []
            cont_epico = cont_lendario = cont_grade6 = 0
            
            if isinstance(data, dict):
                for secao in ["equip", "inven"]:
                    for item in data.get(secao, []):
                        if not isinstance(item, dict):
                            continue
                        
                        nome = item.get("petName")
                        grade = item.get("grade")
                        transcend = item.get("transcend", 1)
                        img = item.get("iconPath")
                        
                        if nome and grade is not None and img and grade >= 4:
                            if grade == 4:
                                cont_epico += 1
                            elif grade == 5:
                                cont_lendario += 1
                            elif grade == 6:
                                cont_grade6 += 1
                            
                            pets.append({
                                "name": nome,
                                "grade": grade,
                                "tier": transcend,
                                "enhance": 0,
                                "count": 1,
                                "img": img,
                                "trade": False
                            })
            
            # Ordenar por grade decrescente
            pets.sort(key=lambda x: (-x["grade"], -x["tier"]))
            
            return pets, cont_epico, cont_lendario, cont_grade6
            
    except Exception as e:
        print(f"Erro ao buscar espíritos: {e}")
    
    return [], 0, 0, 0


def buscar_habilidades_detalhadas(transport_id, class_id):
    """Busca habilidades com imagens corretas"""
    url = f"https://webapi.mir4global.com/nft/character/skills?transportID={transport_id}&class={class_id}&languageCode=pt"
    
    try:
        res = session.get(url, timeout=10)
        if res.ok:
            data = res.json().get("data", [])
            
            habilidades = []
            cont_epico = cont_lendario = 0
            
            if isinstance(data, list):
                classe_nome = CLASSE_PARA_PASTA.get(str(class_id), "guerreiro")
                
                for idx, hab in enumerate(data):
                    if isinstance(hab, dict):
                        nivel = int(hab.get("skillLevel", 0))
                        grade = 5 if nivel >= 10 else (4 if nivel >= 1 else 1)
                        
                        habilidades.append({
                            "name": hab.get("skillName", f"Habilidade {idx+1}"),
                            "grade": grade,
                            "tier": 1,
                            "enhance": nivel,
                            "count": 1,
                            "img": f"/static/skills/{classe_nome}{idx+1}.png",
                            "trade": False
                        })
                        
                        if grade == 5:
                            cont_lendario += 1
                        elif grade == 4:
                            cont_epico += 1
                
                return habilidades, cont_epico, cont_lendario
            
    except Exception as e:
        print(f"Erro ao buscar habilidades: {e}")
    
    return [], 0, 0


def buscar_detalhes_conta(seq, transport_id):
    """Busca todos os detalhes de uma conta"""
    from core.filters import (
        filtrar_itens_comercializaveis, filtrar_itens_especiais,
        processar_equipamento_para_frontend, roman_to_int
    )
    from core.constants import STATUS_DISPONIVEIS
    
    cache_key = f"detalhes_{seq}_equip"
    cached = read_from_cache(cache_key)
    if cached:
        return cached
    
    print(f"[API] Buscando detalhes para conta {seq}")
    
    detalhes = {
        "basic": {},
        "stats": [],
        "codex": 0,
        "potencial": 0,
        "spirit": {"epicos": 0, "lendarios": 0, "grade6": 0},
        "spirit_list": [],
        "training": {"constituicao": 0, "limbo": 0, "inner_force": []},
        "building": {"mina": 0},
        "skills": {"epicas": 0, "lendarias": 0},
        "skills_list": [],
        "equip": [],
        "inven": [],
        "inven_all": [],
        "inven_total": 0,
        "classe": "1",
        "price": 0,
        "tradeType": 1,
        "sealedTS": 0,
        "tickets": [],
        "crystals": [],
        "fragments": []
    }
    
    try:
        # 1. Informações básicas
        url_basic = f"https://webapi.mir4global.com/nft/character/summary?seq={seq}&languageCode=pt"
        res = session.get(url_basic, timeout=15)
        
        if res.ok:
            data = res.json().get("data", {})
            if data:
                character = data.get("character", {})
                if character:
                    detalhes["basic"] = {
                        "name": character.get("name", "Desconhecido"),
                        "worldName": character.get("worldName", "N/A"),
                        "class": character.get("class", "1"),
                        "level": int(character.get("level", 0)),
                        "powerScore": int(character.get("powerScore", 0))
                    }
                    detalhes["classe"] = character.get("class", "1")
                
                try:
                    price_str = str(data.get("price", "0")).replace(',', '').strip()
                    detalhes["price"] = float(price_str) if price_str else 0
                except:
                    detalhes["price"] = 0
                
                # tradeType: 1 = venda direta, 2 = leilão/bidding
                detalhes["tradeType"] = int(data.get("tradeType", 1))
                
                # sealedTS: timestamp de quando foi selado (para calcular tempo de leilão)
                detalhes["sealedTS"] = data.get("sealedTS", 0)
        
        classe = detalhes["classe"]
        
        # 2. Status
        url_stats = f"https://webapi.mir4global.com/nft/character/stats?transportID={transport_id}&languageCode=pt"
        res = session.get(url_stats, timeout=10)
        if res.ok:
            data = res.json().get("data", {})
            if isinstance(data, dict):
                detalhes["stats"] = data.get("lists", [])
                
                for stat in detalhes["stats"]:
                    if isinstance(stat, dict):
                        nome_status = stat.get("statName")
                        if nome_status and nome_status not in STATUS_DISPONIVEIS:
                            STATUS_DISPONIVEIS.append(nome_status)

        # 3. Equipamentos
        equipamentos_raw = buscar_equipamentos_equipados(seq)
        for eq in equipamentos_raw:
            processed = processar_equipamento_para_frontend(eq)
            if processed:
                detalhes["equip"].append(processed)

        # 4. Inventário
        url_inven = f"https://webapi.mir4global.com/nft/character/inven?transportID={transport_id}&languageCode=pt"
        try:
            res = session.get(url_inven, timeout=15)
            if res.ok:
                data = res.json().get("data", [])
                if isinstance(data, list):
                    # Itens comercializáveis (para exibição)
                    itens_filtrados = filtrar_itens_comercializaveis(data)
                    
                    # IDs dos itens comercializáveis para marcar
                    ids_comercializaveis = set()
                    for item in itens_filtrados:
                        ids_comercializaveis.add(item["itemID"])
                    
                    itens_comerciais_frontend = []
                    for item in itens_filtrados:
                        itens_comerciais_frontend.append({
                            "name": item["nome"],
                            "grade": item["grade"],
                            "tier": roman_to_int(item["tier"]),
                            "enhance": item["enhance"],
                            "count": item["quantidade"],
                            "img": item["imagem"],
                            "trade": True
                        })
                    
                    itens_comerciais_frontend.sort(key=lambda x: (-x["grade"], -x["tier"], -x["enhance"]))
                    
                    # TODOS os itens para busca (com flag trade)
                    todos_itens = []
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        item_id = str(item.get("itemID", ""))
                        item_name = item.get("itemName", "")
                        if not item_name:
                            continue
                        
                        grade = int(item.get("grade", "0")) if str(item.get("grade", "0")).isdigit() else 0
                        tier_str = item.get("tier", "I")
                        enhance = int(item.get("enhance", 0)) if str(item.get("enhance", 0)).isdigit() else 0
                        quantidade = item.get("stack", 0) or 1
                        imagem = item.get("itemPath", "")
                        
                        todos_itens.append({
                            "name": item_name,
                            "grade": grade,
                            "tier": roman_to_int(tier_str),
                            "enhance": enhance,
                            "count": quantidade,
                            "img": imagem,
                            "trade": item_id in ids_comercializaveis
                        })
                    
                    todos_itens.sort(key=lambda x: (-x["grade"], -x["tier"], -x["enhance"]))
                    
                    detalhes["inven_all"] = todos_itens
                    detalhes["inven"] = itens_comerciais_frontend[:12]
                    detalhes["inven_total"] = len(itens_comerciais_frontend)
                    
                    bilhetes, cristais, fragmentos = filtrar_itens_especiais(data)
                    detalhes["tickets"] = bilhetes
                    detalhes["crystals"] = cristais
                    detalhes["fragments"] = fragmentos
                    
        except Exception as e:
            print(f"Erro ao buscar inventário: {e}")
        
        # 5. Codex
        url_codex = f"https://webapi.mir4global.com/nft/character/codex?transportID={transport_id}&languageCode=pt"
        try:
            res = session.get(url_codex, timeout=10)
            if res.ok:
                data = res.json().get("data", {})
                if isinstance(data, dict):
                    total = 0
                    for key, item in data.items():
                        if isinstance(item, dict):
                            try:
                                total += int(item.get("completed", "0"))
                            except:
                                pass
                    detalhes["codex"] = total
        except Exception as e:
            print(f"Erro ao buscar codex: {e}")
        
        # 6. Potencial
        url_pot = f"https://webapi.mir4global.com/nft/character/potential?transportID={transport_id}&languageCode=pt"
        try:
            res = session.get(url_pot, timeout=10)
            if res.ok:
                data = res.json().get("data", {})
                if isinstance(data, dict):
                    detalhes["potencial"] = int(data.get("total", 0))
        except Exception as e:
            print(f"Erro ao buscar potencial: {e}")
        
        # 7. Espíritos
        pets, epicos, lendarios, grade6 = buscar_spirit_detalhado(transport_id)
        detalhes["spirit_list"] = pets
        detalhes["spirit"] = {"epicos": epicos, "lendarios": lendarios, "grade6": grade6}
        
        # 8. Treinamento
        url_train = f"https://webapi.mir4global.com/nft/character/training?transportID={transport_id}&languageCode=pt"
        try:
            res = session.get(url_train, timeout=10)
            if res.ok:
                data = res.json().get("data", {})
                if isinstance(data, dict):
                    detalhes["training"]["constituicao"] = int(data.get("consitutionLevel", 0))
                    detalhes["training"]["limbo"] = int(data.get("collectLevel", 0))
                    
                    # Mapear forças por forceIdx
                    for i in range(6):
                        force = data.get(str(i), {})
                        if isinstance(force, dict):
                            force_idx = force.get("forceIdx", "")
                            force_level = int(force.get("forceLevel", 0))
                            force_name = force.get("forceName", f"Força {i+1}")
                            
                            detalhes["training"]["inner_force"].append({
                                "name": force_name,
                                "level": force_level,
                                "idx": force_idx
                            })
                            
                            # Mapear para campos específicos
                            if force_idx == "3001":  # Muscular
                                detalhes["training"]["muscular"] = force_level
                            elif force_idx == "3002":  # Nine Yin
                                detalhes["training"]["noveyin"] = force_level
                            elif force_idx == "3003":  # Nine Yang
                                detalhes["training"]["noveyang"] = force_level
                            elif force_idx == "3006":  # Postura do Sapo
                                detalhes["training"]["sapo"] = force_level
        except Exception as e:
            print(f"Erro ao buscar treinamento: {e}")
        
        # 9. Habilidades
        if classe:
            habilidades, habs_epicas, habs_lendarias = buscar_habilidades_detalhadas(transport_id, classe)
            detalhes["skills_list"] = habilidades
            detalhes["skills"] = {"epicas": habs_epicas, "lendarias": habs_lendarias}
        
        # 10. Mina
        url_building = f"https://webapi.mir4global.com/nft/character/building?transportID={transport_id}&languageCode=pt"
        try:
            res = session.get(url_building, timeout=10)
            if res.ok:
                data = res.json().get("data", {})
                if data:
                    for building_id, building_info in data.items():
                        if str(building_id) == "3000000":
                            try:
                                detalhes["building"]["mina"] = int(building_info.get("buildingLevel", "0"))
                            except ValueError:
                                pass
                            break
        except Exception as e:
            print(f"Erro ao buscar mina: {e}")
            
        save_to_cache(cache_key, detalhes)
        print(f"[SUCESSO] Detalhes salvos para conta {seq}")
        
    except Exception as e:
        print(f"Erro ao buscar detalhes da conta {seq}: {e}")
    
    return detalhes
