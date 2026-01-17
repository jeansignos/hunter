"""
MIR4 Market Hunter - Sistema de Busca de Contas NFT
Versão refatorada com sistema de login e Premium
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from dotenv import load_dotenv

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
            'is_premium': current_user.has_premium_access() if current_user.is_authenticated else False
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
                             is_premium=is_premium)

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
            "itens_comercio_min": request.args.get("itens_comercio_min", type=int),  # NOVO FILTRO
            "status_filtros": {}
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
        
        cache_tipo = request.args.get("cache_tipo", "teste")
        
        # Obter contas do cache
        cache_key = "contas_completas" if cache_tipo == "completas" else "contas_teste"
        contas_com_detalhes = read_from_cache(cache_key) or []
        
        if not contas_com_detalhes:
            return jsonify({
                "success": False,
                "error": "Cache ainda não carregado. Por favor, clique em 'Carregar 10 contas (Teste)' ou 'Carregar Todas'.",
                "cache_carregando": False
            })
        
        # Filtrar contas bloqueadas
        contas_filtradas_cache = [c for c in contas_com_detalhes 
                                   if c.get("basic", {}).get("name", c.get("name", "")) not in NOMES_BLOQUEADOS]
        
        # Aplicar filtros
        contas_filtradas = []
        for conta in contas_filtradas_cache:
            # Filtros básicos (disponíveis para todos)
            classe_conta = str(conta.get("class", "1"))
            if filtros.get("classe") and filtros["classe"] != "0":
                if classe_conta != filtros["classe"]:
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
            
            # Filtros Premium
            if is_premium:
                pets_lendarios = conta.get("spirit", {}).get("lendarios", 0)
                if filtros.get("pets_lendarios_min") and pets_lendarios < filtros["pets_lendarios_min"]:
                    continue
                
                constituicao = conta.get("training", {}).get("constituicao", 0)
                if filtros.get("constituicao_min") and constituicao < filtros["constituicao_min"]:
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
            
            contas_filtradas.append(conta)
        
        # Ordenação
        ordenar_por = request.args.get("ordenar_por", "power")
        ordenar_desc = request.args.get("ordenar_desc", "true").lower() == "true"
        
        if ordenar_por == "power":
            contas_filtradas.sort(key=lambda x: x.get("powerScore", x.get("basic", {}).get("powerScore", 0)), reverse=ordenar_desc)
        elif ordenar_por == "price":
            contas_filtradas.sort(key=lambda x: x.get("price", 0), reverse=ordenar_desc)
        elif ordenar_por == "level":
            contas_filtradas.sort(key=lambda x: x.get("level", x.get("basic", {}).get("level", 0)), reverse=ordenar_desc)
        
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
            aceleramento_mineracao = aumento_aconegro = 0
            
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
            
            conta_formatada = {
                "seq": conta.get("seq"),
                "name": conta.get("basic", {}).get("name", conta.get("name", "Desconhecido")),
                "worldName": conta.get("basic", {}).get("worldName", conta.get("worldName", "N/A")),
                "class": class_info,
                "level": conta.get("level", conta.get("basic", {}).get("level", 0)),
                "powerScore": conta.get("powerScore", conta.get("basic", {}).get("powerScore", 0)),
                "price": price,
                "price_brl": price_brl,
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
                "mina": conta.get("building", {}).get("mina", 0),
                "codex": conta.get("codex", 0),
                "potencial": conta.get("potencial", 0),
                "pets": conta.get("spirit", {"epicos": 0, "lendarios": 0, "grade6": 0}),
                "skills": conta.get("skills", {"epicas": 0, "lendarias": 0}),
                "constituicao": conta.get("training", {}).get("constituicao", 0),
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
