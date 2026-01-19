"""
MIR4 Market Hunter - Sistema de Busca de Contas NFT
Versão refatorada com sistema de login e Premium
"""

import os
import json
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Carregar variáveis de ambiente
load_dotenv()

# Imports do projeto
from config import config
from models import db, User
from blueprints import auth_bp, admin_bp

# Imports das funções originais (mantidas para compatibilidade)
from core.cache import (
    CACHE_DIR, read_from_cache, save_to_cache, 
    limpar_cache_contas, limpar_todo_cache
)
from core.api import (
    buscar_lista_contas, buscar_todas_contas, buscar_detalhes_conta,
    get_wemix_brl_price, session
)
from core.filters import (
    filtrar_itens_comercializaveis, filtrar_itens_especiais,
    formatar_valor, hash_status
)
from core.constants import (
    CLASSES, STATUS_MINERACAO, STATUS_DISPONIVEIS,
    NOMES_BLOQUEADOS, CACHE_EXPIRY_MINUTES
)


def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    
    # Inicializar CSRF protection
    csrf = CSRFProtect(app)
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        
        # Criar admin padrão se não existir
        admin = User.query.filter_by(email='admin@mir4market.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@mir4market.com',
                is_admin=True,
                is_premium=True
            )
            admin.set_password('admin123')  # MUDAR EM PRODUÇÃO!
            db.session.add(admin)
            db.session.commit()
            print("[SETUP] Admin padrão criado: admin@mir4market.com / admin123")
    
    # ==================== VARIÁVEIS GLOBAIS ====================
    cache_carregando = False
    contas_em_cache = False
    
    # ==================== CONTEXT PROCESSORS ====================
    @app.context_processor
    def inject_user():
        """Injeta variáveis úteis em todos os templates"""
        return {
            'current_user': current_user,
            'is_premium': current_user.has_premium_access() if current_user.is_authenticated else False,
            'is_admin': current_user.is_admin if current_user.is_authenticated else False
        }
    
    # ==================== ROTAS PRINCIPAIS ====================
    @app.route("/")
    def index():
        """Página principal com filtros"""
        status_cache = read_from_cache("status_disponiveis") or []
        
        status_importantes = []
        for status in STATUS_MINERACAO:
            status_hash = hash_status(status)
            nome_exibicao = "Aceleramento de Mineração" if status == "Aceleramento de Tempo de Mineração" else status
            status_importantes.append({
                "nome": nome_exibicao,
                "nome_completo": status,
                "hash": status_hash,
                "destaque": True
            })
        
        outros_status = []
        for status in status_cache:
            if status in STATUS_MINERACAO:
                continue
            status_hash = hash_status(status)
            outros_status.append({
                "nome": status,
                "nome_completo": status,
                "hash": status_hash,
                "destaque": False
            })
        
        outros_status = sorted(outros_status, key=lambda x: x["nome"])[:40]
        status_importantes.extend(outros_status)
        
        cache_completo = read_from_cache("contas_completas")
        cache_teste = read_from_cache("contas_teste")
        
        tem_cache_completo = bool(cache_completo)
        tem_cache_teste = bool(cache_teste)
        cache_padrao = "completas" if tem_cache_completo else ("teste" if tem_cache_teste else None)
        
        total_completo = len(cache_completo) if cache_completo else 0
        total_teste = len(cache_teste) if cache_teste else 0
        cache_status = "completo" if tem_cache_completo else ("teste" if tem_cache_teste else "vazio")
        
        # Verificar se usuário tem acesso premium
        is_premium = current_user.has_premium_access() if current_user.is_authenticated else False
        
        # Carregar lista de itens para o modal de filtro
        itens_lista = []
        try:
            itens_path = os.path.join(app.static_folder, 'itens_lista.json')
            if os.path.exists(itens_path):
                with open(itens_path, 'r', encoding='utf-8') as f:
                    itens_lista = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar itens_lista.json: {e}")
        
        return render_template("index_filtro.html", 
                             classes=CLASSES, 
                             status_importantes=status_importantes,
                             cache_status=cache_status,
                             tem_cache_completo=tem_cache_completo,
                             tem_cache_teste=tem_cache_teste,
                             cache_padrao=cache_padrao,
                             total_completo=total_completo,
                             total_teste=total_teste,
                             STATUS_MINERACAO=STATUS_MINERACAO,
                             is_premium=is_premium,
                             itens_lista=itens_lista)

    @app.route("/buscar-contas", methods=["GET"])
    def buscar_contas_rota():
        """Busca contas com filtros - Importa lógica do arquivo original"""
        import time
        inicio = time.time()
        
        # Verificar se usuário tem acesso premium para filtros avançados
        is_premium = current_user.has_premium_access() if current_user.is_authenticated else False
        
        filtros = {
            "classe": request.args.get("classe", "0"),
            "power_min": request.args.get("power_min", type=int),
            "power_max": request.args.get("power_max", type=int),
            "level_min": request.args.get("level_min", type=int),
            "level_max": request.args.get("level_max", type=int),
            "price_min": request.args.get("price_min", type=float),
            "price_max": request.args.get("price_max", type=float),
            "codex_min": request.args.get("codex_min", type=int),
            "potencial_min": request.args.get("potencial_min", type=int),
            "pets_lendarios_min": request.args.get("pets_lendarios_min", type=int),
            "pets_misticos_min": request.args.get("pets_misticos_min", type=int),
            "habs_lendarias_min": request.args.get("habs_lendarias_min", type=int),
            "constituicao_min": request.args.get("constituicao_min", type=int),
            "mina_min": request.args.get("mina_min", type=int),
            "itens_comercio_min": request.args.get("itens_comercio_min", type=int),
            "regiao": request.args.get("regiao"),
            "servidor": request.args.get("servidor"),
            # NOVOS FILTROS
            "busca_nome": request.args.get("busca_nome"),
            "nome_jogador": request.args.get("nome_jogador"),
            "status_lance": request.args.get("status_lance"),  # listado/bidding
            # Treino
            "treino_constituicao": request.args.get("treino_constituicao", type=int),
            "treino_muscular": request.args.get("treino_muscular", type=int),
            "treino_noveyin": request.args.get("treino_noveyin", type=int),
            "treino_noveyang": request.args.get("treino_noveyang", type=int),
            "treino_sapo": request.args.get("treino_sapo", type=int),
            # Outros
            "potencial_min": request.args.get("potencial_min", type=int),
            "espiritos": request.args.get("espiritos"),  # Lista de nomes separados por vírgula
            # Trade (itens comercializáveis)
            "equip_lend_trade_min": request.args.get("equip_lend_trade_min", type=int),
            "equip_epic_trade_min": request.args.get("equip_epic_trade_min", type=int),
            # Skills/Habilidades (JSON)
            "skills_filtro": request.args.get("skills_filtro"),
            "status_filtros": {},
            "itens_filtros": {}
        }
        
        # Filtros Premium - só aplicar se usuário tiver acesso
        if is_premium:
            status_disponiveis = read_from_cache("status_disponiveis") or []
            for status in status_disponiveis:
                status_hash = hash_status(status)
                valor_min = request.args.get(f"status_{status_hash}", type=float)
                if valor_min is not None:
                    filtros["status_filtros"][status] = valor_min
            
            status_mineracao_map = {
                "Aceleramento de Tempo de Mineração": "status_aceleramento",
                "Aumento de Ganho de Aço Negro": "status_aconegro"
            }
            
            for status_nome, input_id in status_mineracao_map.items():
                valor_min = request.args.get(input_id, type=float)
                if valor_min is not None:
                    filtros["status_filtros"][status_nome] = valor_min
            
            # Coletar filtros de itens
            for key, value in request.args.items():
                if key.startswith('item_'):
                    try:
                        qtd_min = int(value)
                        if qtd_min > 0:
                            item_hash = key.replace('item_', '')
                            filtros["itens_filtros"][item_hash] = qtd_min
                    except (ValueError, TypeError):
                        pass
        
        cache_tipo = request.args.get("cache_tipo", "teste")
        
        # Obter contas do cache
        cache_key = "contas_completas" if cache_tipo == "completas" else "contas_teste"
        contas_com_detalhes = read_from_cache(cache_key) or []
        
        # Se não tem cache, busca diretamente da API (modo básico)
        if not contas_com_detalhes:
            from core.api import buscar_todas_contas
            try:
                contas_api = buscar_todas_contas(max_paginas=1)  # Só primeira página
                if contas_api:
                    # Formatar contas da API para o mesmo formato do cache
                    contas_com_detalhes = []
                    for c in contas_api[:20]:  # Máximo 20 contas sem cache
                        conta_formatada = {
                            "seq": c.get("seq"),
                            "transportID": c.get("transportID"),
                            "class": c.get("class", 1),
                            "name": c.get("characterName", ""),
                            "worldName": c.get("worldName", ""),
                            "lv": c.get("lv", 1),
                            "powerScore": c.get("powerScore", 0),
                            "price": c.get("price", 0),
                            "tradeType": c.get("tradeType", 1),
                            "nftID": c.get("nftID", ""),
                            "basic": c,
                            "sem_cache": True  # Marcador para indicar dados básicos
                        }
                        contas_com_detalhes.append(conta_formatada)
            except Exception as e:
                print(f"Erro ao buscar da API: {e}")
        
        if not contas_com_detalhes:
            return jsonify({
                "success": False,
                "error": "Não foi possível carregar contas. Tente novamente.",
                "cache_carregando": False
            })
        
        # Filtrar contas bloqueadas
        contas_filtradas_cache = [c for c in contas_com_detalhes 
                                   if c.get("basic", {}).get("name", c.get("name", "")) not in NOMES_BLOQUEADOS]
        
        # Buscar nftIDs com bid ativo do wemixplay (se filtro bidding estiver ativo)
        nft_ids_com_bid = set()
        if filtros.get("status_lance") in ["bidding", "listado"]:
            from core.api import obter_contas_com_bid_cached
            try:
                _, nft_ids_com_bid, _ = obter_contas_com_bid_cached()
                print(f"[FILTRO] {len(nft_ids_com_bid)} contas com bid ativo no wemixplay")
            except Exception as e:
                print(f"[FILTRO] Erro ao buscar nftIDs com bid: {e}")

        # Aplicar filtros
        contas_filtradas = []
        for conta in contas_filtradas_cache:
            # Filtros básicos (disponíveis para todos)
            classe_conta = str(conta.get("class", "1"))
            if filtros.get("classe") and filtros["classe"] != "0":
                if classe_conta != filtros["classe"]:
                    continue
            
            # Filtro por nome do jogador
            if filtros.get("nome_jogador") and filtros["nome_jogador"]:
                nome_conta = conta.get("name", conta.get("basic", {}).get("name", "")).lower()
                nome_busca = filtros["nome_jogador"].lower()
                if nome_busca not in nome_conta:
                    continue
            
            # Filtro por status de lance (usando dados em tempo real do wemixplay)
            status_lance = filtros.get("status_lance")
            if status_lance:
                nft_id = str(conta.get("nftID", ""))
                if status_lance == "bidding":
                    # Usar dados do wemixplay para verificar se tem bid ativo
                    if nft_id not in nft_ids_com_bid:
                        continue
                elif status_lance == "listado":
                    # Mostrar apenas contas SEM bid ativo
                    if nft_id in nft_ids_com_bid:
                        continue
            
            # Filtro de servidor
            world_name = conta.get("worldName", conta.get("basic", {}).get("worldName", ""))
            if filtros.get("servidor") and filtros["servidor"]:
                if world_name != filtros["servidor"]:
                    continue
            elif filtros.get("regiao") and filtros["regiao"]:
                # Se só tem região, filtra pelos servidores daquela região
                regiao_servidores = {
                    "ASIA1": ["ASIA011", "ASIA012", "ASIA013", "ASIA014", "ASIA021", "ASIA022", "ASIA023", "ASIA024", "ASIA031", "ASIA032", "ASIA033", "ASIA041", "ASIA042", "ASIA043"],
                    "ASIA2": ["ASIA051", "ASIA052", "ASIA053", "ASIA054", "ASIA061", "ASIA062", "ASIA063", "ASIA064", "ASIA071", "ASIA072", "ASIA073", "ASIA081", "ASIA082", "ASIA083"],
                    "ASIA3": ["ASIA311", "ASIA312", "ASIA313", "ASIA314", "ASIA321", "ASIA322", "ASIA323", "ASIA324", "ASIA331", "ASIA332", "ASIA333", "ASIA341", "ASIA342", "ASIA343"],
                    "ASIA4": ["ASIA351", "ASIA352", "ASIA353", "ASIA354", "ASIA361", "ASIA362", "ASIA363", "ASIA364", "ASIA371", "ASIA372", "ASIA373"],
                    "INMENA1": ["INMENA011", "INMENA012", "INMENA013", "INMENA014", "INMENA021", "INMENA022", "INMENA023", "INMENA024"],
                    "EU1": ["EU011", "EU012", "EU013", "EU014", "EU021", "EU022", "EU023", "EU024", "EU031", "EU032", "EU033", "EU034", "EU041", "EU042", "EU043"],
                    "SA1": ["SA011", "SA012", "SA013", "SA014", "SA021", "SA022", "SA023", "SA031", "SA032", "SA033", "SA034", "SA041", "SA043", "SA044"],
                    "SA2": ["SA051", "SA052", "SA053", "SA054", "SA061", "SA062", "SA064", "SA071", "SA072", "SA073", "SA081", "SA082", "SA083"],
                    "NA1": ["NA011", "NA012", "NA013", "NA014", "NA021", "NA022", "NA023", "NA031", "NA032", "NA033", "NA034", "NA042", "NA043", "NA044"],
                    "NA2": ["NA051", "NA052", "NA053", "NA054", "NA061", "NA062", "NA071", "NA072", "NA073", "NA074", "NA081", "NA082", "NA083", "NA084"]
                }
                servidores_regiao = regiao_servidores.get(filtros["regiao"], [])
                if servidores_regiao and world_name not in servidores_regiao:
                    continue
            
            power = conta.get("powerScore", conta.get("basic", {}).get("powerScore", 0))
            if filtros.get("power_min") and power < filtros["power_min"]:
                continue
            if filtros.get("power_max") and power > filtros["power_max"]:
                continue
            
            level = conta.get("level", conta.get("basic", {}).get("level", 0))
            if filtros.get("level_min") and level < filtros["level_min"]:
                continue
            if filtros.get("level_max") and level > filtros["level_max"]:
                continue
            
            price = conta.get("price", 0)
            if filtros.get("price_min") and price < filtros["price_min"]:
                continue
            if filtros.get("price_max") and price > filtros["price_max"]:
                continue
            
            mina_level = conta.get("building", {}).get("mina", 0)
            if filtros.get("mina_min") and mina_level < filtros["mina_min"]:
                continue
            
            codex = conta.get("codex", 0)
            if filtros.get("codex_min") and codex < filtros["codex_min"]:
                continue
            
            # NOVO FILTRO: Itens de comércio (2+)
            if filtros.get("itens_comercio_min"):
                total_itens = conta.get("inven_total", 0)
                # Contar itens épicos e lendários
                itens_all = conta.get("inven_all", [])
                itens_valiosos = [i for i in itens_all if i.get("grade", 0) >= 4]  # Grade 4+ = Épico/Lendário
                if len(itens_valiosos) < filtros["itens_comercio_min"]:
                    continue
            
            # NOVO FILTRO: Equipamentos Trade (comercializáveis com balança)
            if filtros.get("equip_lend_trade_min") or filtros.get("equip_epic_trade_min"):
                equipamentos = conta.get("equip", [])
                lend_trade_count = sum(1 for e in equipamentos if e.get("trade") and e.get("grade") == 5)
                epic_trade_count = sum(1 for e in equipamentos if e.get("trade") and e.get("grade") == 4)
                
                if filtros.get("equip_lend_trade_min") and lend_trade_count < filtros["equip_lend_trade_min"]:
                    continue
                if filtros.get("equip_epic_trade_min") and epic_trade_count < filtros["equip_epic_trade_min"]:
                    continue
            
            # NOVO FILTRO: Nome do jogador
            if filtros.get("nome_jogador"):
                nome_conta = conta.get("basic", {}).get("name", conta.get("name", ""))
                if filtros["nome_jogador"].lower() not in nome_conta.lower():
                    continue
            
            # Filtros Premium
            if is_premium:
                pets_lendarios = conta.get("spirit", {}).get("lendarios", 0)
                if filtros.get("pets_lendarios_min") and pets_lendarios < filtros["pets_lendarios_min"]:
                    continue
                
                # Filtros de Treino
                training = conta.get("training", {})
                
                constituicao = training.get("constituicao", 0)
                if filtros.get("treino_constituicao") and constituicao < filtros["treino_constituicao"]:
                    continue
                # Também verificar filtro antigo
                if filtros.get("constituicao_min") and constituicao < filtros["constituicao_min"]:
                    continue
                
                muscular = training.get("muscular", 0)
                if filtros.get("treino_muscular") and muscular < filtros["treino_muscular"]:
                    continue
                
                noveyin = training.get("noveyin", 0)
                if filtros.get("treino_noveyin") and noveyin < filtros["treino_noveyin"]:
                    continue
                
                noveyang = training.get("noveyang", 0)
                if filtros.get("treino_noveyang") and noveyang < filtros["treino_noveyang"]:
                    continue
                
                sapo = training.get("sapo", 0)
                if filtros.get("treino_sapo") and sapo < filtros["treino_sapo"]:
                    continue
                
                habs_lendarias = conta.get("skills", {}).get("lendarias", 0)
                if filtros.get("habs_lendarias_min") and habs_lendarias < filtros["habs_lendarias_min"]:
                    continue
                
                pets_misticos = conta.get("spirit", {}).get("grade6", 0)
                if filtros.get("pets_misticos_min") and pets_misticos < filtros["pets_misticos_min"]:
                    continue
                
                potencial = conta.get("potencial", 0)
                if filtros.get("potencial_min") and potencial < filtros["potencial_min"]:
                    continue
                
                # Filtros de status
                if filtros["status_filtros"]:
                    stats_list = conta.get("stats", [])
                    stats_dict = {}
                    for stat in stats_list:
                        if isinstance(stat, dict):
                            stat_name = stat.get("statName", "")
                            stat_value = stat.get("statValue", "0")
                            stats_dict[stat_name] = formatar_valor(stat_value)
                    
                    passa_nos_filtros = True
                    for status_nome, valor_min in filtros["status_filtros"].items():
                        if stats_dict.get(status_nome, 0) < valor_min:
                            passa_nos_filtros = False
                            break
                    
                    if not passa_nos_filtros:
                        continue
                
                # Filtros de itens específicos
                if filtros["itens_filtros"]:
                    # Carregar lista de itens para fazer o mapeamento hash -> nome
                    import os as os_local
                    itens_lista = []
                    try:
                        itens_path = os_local.path.join(app.static_folder, 'itens_lista.json')
                        if os_local.path.exists(itens_path):
                            with open(itens_path, 'r', encoding='utf-8') as f_itens:
                                itens_lista = json.load(f_itens)
                    except:
                        pass
                    
                    # Criar mapeamento hash -> nome
                    hash_to_nome = {item["hash"]: item["nome"] for item in itens_lista}
                    
                    # Obter inventário completo da conta
                    inventario = conta.get("inven_all", [])
                    
                    # Contar itens por nome (usando os campos corretos: name e count)
                    contagem_itens = {}
                    for item in inventario:
                        if isinstance(item, dict):
                            nome_item = item.get("name", "")
                            quantidade = item.get("count", 1)
                            if quantidade == 0:
                                quantidade = 1
                            contagem_itens[nome_item] = contagem_itens.get(nome_item, 0) + quantidade
                    
                    # Verificar se passa nos filtros de itens
                    passa_nos_itens = True
                    for item_hash, qtd_min in filtros["itens_filtros"].items():
                        nome_item = hash_to_nome.get(item_hash, "")
                        if nome_item:
                            qtd_atual = contagem_itens.get(nome_item, 0)
                            if qtd_atual < qtd_min:
                                passa_nos_itens = False
                                break
                    
                    if not passa_nos_itens:
                        continue
                
                # Filtro de Espíritos específicos
                if filtros.get("espiritos"):
                    espiritos_desejados = [e.strip() for e in filtros["espiritos"].split(",")]
                    spirit_list = conta.get("spirit_list", [])
                    nomes_espiritos = [s.get("name", "") for s in spirit_list if isinstance(s, dict)]
                    
                    # Verificar se a conta tem TODOS os espíritos selecionados
                    tem_todos = True
                    for espirito in espiritos_desejados:
                        # Busca parcial (contém)
                        encontrado = any(espirito.lower() in nome.lower() for nome in nomes_espiritos)
                        if not encontrado:
                            tem_todos = False
                            break
                    
                    if not tem_todos:
                        continue
                
                # Filtro de Skills/Habilidades
                if filtros.get("skills_filtro"):
                    try:
                        skills_requeridas = json.loads(filtros["skills_filtro"])
                        skills_list = conta.get("skills_list", [])
                        classe_conta = str(conta.get("class", "1"))
                        
                        passa_skills = True
                        for skill_req in skills_requeridas:
                            # Verificar se a classe bate
                            if str(skill_req.get("classe")) != classe_conta:
                                passa_skills = False
                                break
                            
                            # Buscar a skill pelo índice (1-13)
                            idx = skill_req.get("idx", 0)
                            nivel_min = skill_req.get("nivelMin", 8)
                            
                            # skills_list é uma lista ordenada de skills
                            if idx > 0 and idx <= len(skills_list):
                                skill = skills_list[idx - 1]
                                # O nível da skill está no campo 'enhance'
                                nivel_skill = skill.get("enhance", 0) if isinstance(skill, dict) else 0
                                if nivel_skill < nivel_min:
                                    passa_skills = False
                                    break
                            else:
                                passa_skills = False
                                break
                        
                        if not passa_skills:
                            continue
                    except json.JSONDecodeError:
                        pass
            
            contas_filtradas.append(conta)
        
        # Ordenação
        ordenar_por = request.args.get("ordenar_por", "power")
        ordenar_desc = request.args.get("ordenar_desc", "true").lower() == "true"
        
        # Função auxiliar para obter valor de um stat pelo nome
        def get_stat_value(conta, stat_name):
            """Retorna o valor de um stat específico"""
            for stat in conta.get("stats", []):
                if isinstance(stat, dict):
                    name = stat.get("statName", "").upper()
                    if stat_name.upper() in name:
                        try:
                            val = stat.get("statValue", "0")
                            if isinstance(val, str):
                                val = val.replace(",", "").replace("%", "")
                            return float(val)
                        except:
                            return 0
            return 0
        
        if ordenar_por == "power":
            contas_filtradas.sort(key=lambda x: x.get("powerScore", x.get("basic", {}).get("powerScore", 0)), reverse=ordenar_desc)
        elif ordenar_por == "price":
            contas_filtradas.sort(key=lambda x: x.get("price", 0), reverse=ordenar_desc)
        elif ordenar_por == "level":
            contas_filtradas.sort(key=lambda x: x.get("level", x.get("basic", {}).get("level", 0)), reverse=ordenar_desc)
        elif ordenar_por == "critico":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "CRÍTICO"), reverse=ordenar_desc)
        elif ordenar_por == "evasao":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "EVASÃO"), reverse=ordenar_desc)
        elif ordenar_por == "ataque_fisico":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "ATAQUE FÍSICO"), reverse=ordenar_desc)
        elif ordenar_por == "ataque_magico":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "ATAQUE DE FEITIÇO"), reverse=ordenar_desc)
        elif ordenar_por == "precisao":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "PRECISÃO"), reverse=ordenar_desc)
        elif ordenar_por == "derrubada":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "AUMENTO DA PROBABILIDADE DE SUCESSO DE DERRUBAR"), reverse=ordenar_desc)
        elif ordenar_por == "evasao_critico":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "EVASÃO DE CRÍTICO"), reverse=ordenar_desc)
        elif ordenar_por == "atk_habilidade":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "AUMENTO DE ATK DE HABILIDADE"), reverse=ordenar_desc)
        elif ordenar_por == "aceleramento":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "ACELERAMENTO DE TEMPO DE MINERAÇÃO"), reverse=ordenar_desc)
        elif ordenar_por == "aconegro":
            contas_filtradas.sort(key=lambda x: get_stat_value(x, "AUMENTO DE GANHO DE AÇO NEGRO"), reverse=ordenar_desc)
        elif ordenar_por == "codex":
            contas_filtradas.sort(key=lambda x: x.get("codex", 0), reverse=ordenar_desc)
        elif ordenar_por == "mina":
            contas_filtradas.sort(key=lambda x: x.get("building", {}).get("mina", 0), reverse=ordenar_desc)
        elif ordenar_por == "constituicao":
            contas_filtradas.sort(key=lambda x: x.get("training", {}).get("constituicao", 0), reverse=ordenar_desc)
        
        # Paginação
        pagina = request.args.get("pagina", 0, type=int)
        limite = request.args.get("limite", 10, type=int)
        offset = pagina * limite
        
        total_filtrado = len(contas_filtradas)
        contas_paginadas = contas_filtradas[offset:offset + limite] if offset < len(contas_filtradas) else []
        
        wemix_brl = get_wemix_brl_price()
        
        # Formatar contas para resposta
        contas_formatadas = []
        for conta in contas_paginadas:
            classe_id = str(conta.get("class", conta.get("classe", "1")))
            class_info = CLASSES.get(classe_id, CLASSES["1"])
            
            price = conta.get("price", 0)
            price_brl = round(price * wemix_brl, 2) if wemix_brl and price > 0 else None
            
            # Extrair stats importantes
            stats = conta.get("stats", [])
            ataque_fisico = ataque_magico = critico = precisao = evasao = 0
            aceleramento_mineracao = aumento_aconegro = atk_habilidade = 0
            
            for stat in stats:
                if isinstance(stat, dict):
                    stat_name = stat.get("statName", "").upper()
                    valor = formatar_valor(stat.get("statValue", "0"))
                    
                    if "ATAQUE FÍSICO" in stat_name:
                        ataque_fisico = valor
                    elif "ATAQUE DE FEITIÇO" in stat_name:
                        ataque_magico = valor
                    elif stat_name.strip() == "CRÍTICO":
                        critico = valor
                    elif stat_name.strip() == "PRECISÃO":
                        precisao = valor
                    elif stat_name.strip() == "EVASÃO":
                        evasao = valor
                    elif "ACELERAMENTO" in stat_name and "MINERAÇÃO" in stat_name:
                        aceleramento_mineracao = valor
                    elif "AUMENTO DE GANHO DE AÇO NEGRO" in stat_name:
                        aumento_aconegro = valor
                    elif "DANO DE ATAQUE" in stat_name and "HABILIDADE" in stat_name:
                        atk_habilidade = valor
            
            conta_formatada = {
                "seq": conta.get("seq"),
                "name": conta.get("basic", {}).get("name", conta.get("name", "Desconhecido")),
                "worldName": conta.get("basic", {}).get("worldName", conta.get("worldName", "N/A")),
                "class": class_info,
                "level": conta.get("level", conta.get("basic", {}).get("level", 0)),
                "powerScore": conta.get("powerScore", conta.get("basic", {}).get("powerScore", 0)),
                "price": price,
                "price_brl": price_brl,
                "tradeType": conta.get("tradeType", 1),
                "sealedTS": conta.get("sealedTS", 0),
                "nftID": conta.get("nftID", ""),
                "bid_count": conta.get("bid_count", 0),
                "auctionEndTime": conta.get("auctionEndTime", 0),
                "equip": conta.get("equip", []),
                "inven": conta.get("inven", []),
                "inven_all": conta.get("inven_all", []),
                "inven_total": conta.get("inven_total", 0),
                "spirit_list": conta.get("spirit_list", []),
                "skills_list": conta.get("skills_list", []),
                "ataque_fisico": ataque_fisico,
                "ataque_magico": ataque_magico,
                "critico": critico,
                "precisao": precisao,
                "evasao": evasao,
                "aceleramento_mineracao": aceleramento_mineracao,
                "aumento_aconegro": aumento_aconegro,
                "atk_habilidade": atk_habilidade,
                "mina": conta.get("building", {}).get("mina", 0),
                "codex": conta.get("codex", 0),
                "potencial": conta.get("potencial", 0),
                "pets": conta.get("spirit", {"epicos": 0, "lendarios": 0, "grade6": 0}),
                "skills": conta.get("skills", {"epicas": 0, "lendarias": 0}),
                "constituicao": conta.get("training", {}).get("constituicao", 0),
                "training_details": conta.get("training", {"constituicao": 0, "inner_force": []}),
                "stats": conta.get("stats", []),
                "url": f"https://www.xdraco.com/nft/trade/{conta.get('seq')}",
                "tickets": conta.get("tickets", []),
                "crystals": conta.get("crystals", []),
                "fragments": conta.get("fragments", [])
            }
            contas_formatadas.append(conta_formatada)
        
        tempo_total = time.time() - inicio
        return jsonify({
            "success": True,
            "contas": contas_formatadas,
            "total": len(contas_paginadas),
            "total_filtrado": total_filtrado,
            "tempo": round(tempo_total, 2),
            "wemix_brl": wemix_brl,
            "total_cache": len(contas_com_detalhes),
            "cache_tipo": cache_tipo,
            "is_premium": is_premium
        })

    # ==================== ROTAS DE CACHE ====================
    @app.route("/carregar-teste", methods=["POST"])
    @csrf.exempt
    def carregar_teste():
        """Inicia carregamento de teste (10 contas)"""
        import threading
        from core.loader import carregar_contas_teste
        
        threading.Thread(target=carregar_contas_teste, daemon=True).start()
        
        return jsonify({
            "success": True,
            "message": "Carregamento de teste (10 contas) iniciado."
        })

    @app.route("/carregar-completo", methods=["POST"])
    @csrf.exempt
    def carregar_completo():
        """Inicia carregamento completo de todas as contas"""
        import threading
        from core.loader import carregar_contas_completas
        
        threading.Thread(target=carregar_contas_completas, daemon=True).start()
        
        return jsonify({
            "success": True,
            "message": "Carregamento completo iniciado. Isso pode levar vários minutos."
        })

    @app.route("/status-carregamento")
    def status_carregamento():
        """Retorna status do carregamento de cache"""
        from core.loader import cache_carregando, get_progresso
        
        cache_completo = read_from_cache("contas_completas")
        cache_teste = read_from_cache("contas_teste")
        progresso = get_progresso()
        
        return jsonify({
            "carregando": cache_carregando,
            "tem_cache_completo": cache_completo is not None,
            "total_completo": len(cache_completo) if cache_completo else 0,
            "tem_cache_teste": cache_teste is not None,
            "total_teste": len(cache_teste) if cache_teste else 0,
            "progresso": progresso
        })

    @app.route("/limpar-cache")
    def limpar_cache():
        """Limpa todo o cache"""
        if limpar_todo_cache():
            return "Cache limpo com sucesso!"
        return "Erro ao limpar cache."

    @app.route("/limpar-cache-contas")
    def limpar_cache_contas_rota():
        """Limpa apenas cache de contas"""
        if limpar_cache_contas():
            return "Cache de contas limpo com sucesso!"
        return "Erro ao limpar cache de contas."

    @app.route("/api/contas-com-bid")
    def api_contas_com_bid():
        """Retorna lista de contas com bid ativo do wemixplay (com cache de 20 min)"""
        from core.api import obter_contas_com_bid_cached, get_cache_bid_status
        force = request.args.get("force", "false").lower() == "true"
        try:
            contas, nft_ids, from_cache = obter_contas_com_bid_cached(force_refresh=force)
            cache_status = get_cache_bid_status()
            return jsonify({
                "success": True,
                "total": len(contas),
                "contas": contas,
                "nftIDs": list(nft_ids),
                "from_cache": from_cache,
                "cache": cache_status
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/api/verificar-conta-ativa/<nft_id>")
    def api_verificar_conta_ativa(nft_id):
        """Verifica se conta ainda está em leilão (para quando cronômetro zerar)"""
        from core.api import verificar_conta_ainda_ativa
        try:
            resultado = verificar_conta_ainda_ativa(nft_id)
            return jsonify({
                "success": True,
                **resultado
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/api/cache-bid-status")
    def api_cache_bid_status():
        """Retorna status do cache de bids"""
        from core.api import get_cache_bid_status
        try:
            status = get_cache_bid_status()
            return jsonify({
                "success": True,
                **status
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


    @app.route("/api/verificar-lance/<nft_id>")
    def verificar_lance(nft_id):
        """Verifica status de lance em tempo real do wemixplay"""
        from core.api import buscar_status_lance_wemixplay
        try:
            status = buscar_status_lance_wemixplay(nft_id)
            return jsonify({
                "success": True,
                "nftID": nft_id,
                "status": status
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/debug-contas-lance")
    def debug_contas_lance():
        """Debug: verifica quantas contas com lance existem no cache"""
        cache_completo = read_from_cache("contas_completas") or []
        cache_teste = read_from_cache("contas_teste") or []
        
        total_completo = len(cache_completo)
        total_teste = len(cache_teste)
        
        # Contar por tradeType
        bidding_completo = sum(1 for c in cache_completo if c.get("tradeType") == 2)
        listado_completo = sum(1 for c in cache_completo if c.get("tradeType") == 1)
        sem_tipo_completo = sum(1 for c in cache_completo if c.get("tradeType") not in [1, 2])
        
        bidding_teste = sum(1 for c in cache_teste if c.get("tradeType") == 2)
        listado_teste = sum(1 for c in cache_teste if c.get("tradeType") == 1)
        
        return jsonify({
            "cache_completo": {
                "total": total_completo,
                "listado (tradeType=1)": listado_completo,
                "bidding (tradeType=2)": bidding_completo,
                "sem_tipo": sem_tipo_completo
            },
            "cache_teste": {
                "total": total_teste,
                "listado (tradeType=1)": listado_teste,
                "bidding (tradeType=2)": bidding_teste
            }
        })

    return app


# Criar aplicação
app = create_app()


if __name__ == "__main__":
    print("=" * 60)
    print("MIR4 Market Hunter - Sistema de Busca de Contas NFT")
    print("=" * 60)
    print("Rotas disponíveis:")
    print("  / - Página principal")
    print("  /auth/login - Login")
    print("  /auth/register - Registro")
    print("  /admin/ - Painel administrativo")
    print("=" * 60)
    
    app.run(debug=True, host="0.0.0.0", port=5001)
