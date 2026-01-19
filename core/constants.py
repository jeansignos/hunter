"""
Constantes e configurações do sistema
"""

# ==================== CONFIGURAÇÃO DE BLOQUEIO ====================
NOMES_BLOQUEADOS = [
    "DeLtaシ",
    "快乐丶小 K"
]

# ==================== CONFIGURAÇÃO DE CACHE ====================
CACHE_DIR = "xdraco_cache_status"
CACHE_EXPIRY_MINUTES = 720
CACHE_STATUS_EXPIRY = 1440

# ==================== LISTAS DE STATUS ====================
STATUS_DISPONIVEIS = []

STATUS_MINERACAO = [
    "Aceleramento de Tempo de Mineração",
    "Aumento de Ganho de Aço Negro",
    "Mina"
]

# ==================== CLASSES ====================
CLASSES = {
    "1": {
        "nome": "Guerreiro", 
        "icone": "⚔️", 
        "cor": "#fbbf24",
        "imagem": "class_warrior.png",
        "nome_api": "warrior"
    },
    "2": {
        "nome": "Maga", 
        "icone": "🔮", 
        "cor": "#8b5cf6",
        "imagem": "classe2.png",
        "nome_api": "sorcerer"
    },
    "3": {
        "nome": "Taoísta",
        "icone": "☯️", 
        "cor": "#10b981",
        "imagem": "class_taoist.png",
        "nome_api": "taoist"
    },
    "4": {
        "nome": "Arqueira",
        "icone": "🏹", 
        "cor": "#ef4444",
        "imagem": "class_arbalist.png",
        "nome_api": "arbalist"
    },
    "5": {
        "nome": "Lanceiro", 
        "icone": "🔱", 
        "cor": "#6366f1",
        "imagem": "class_lancer.png",
        "nome_api": "lancer"
    },
    "6": {
        "nome": "Soturna",
        "icone": "⚙️", 
        "cor": "#8b5cf6",
        "imagem": "class_engineer.png",
        "nome_api": "darkist"
    },
    "7": {
        "nome": "Coração de Leão", 
        "icone": "🦁", 
        "cor": "#f59e0b",
        "imagem": "leao.png",
        "nome_api": "warrior"
    }
}

# Mapeamento para habilidades
CLASSE_PARA_PASTA = {
    "1": "guerreiro",
    "2": "maga", 
    "3": "taoista",
    "4": "lanceiro",
    "5": "arqueira",
    "6": "soturna",
    "7": "guerreiro"
}

# ==================== LISTAS DE ITENS ESPECIAIS ====================
BILHETES_NOMES = [
    "Bilhete de Pico Secreto",
    "Bilhete de Praça Mágica", 
    "Bilhete de Raide Infernal",
    "Bilhete de Raide de Boss",
    "Bilhete de Raide",
    "Bilhete do Caminho do Treino Intenso"
]

CRISTAIS_NOMES = [
    "Cristal da Alma Esvoaçante Épico",
    "Cristal da Alma Esvoaçante Raro",
    "Cristal da Alma Esvoaçante Incomum",
    "Cristal de Quintessência Épico",
    "Cristal de Quintessência Raro", 
    "Cristal de Quintessência Incomum",
    "Cristal da Alma Celestial Épico",
    "Cristal da Alma Celestial Raro",
    "Cristal da Alma Celestial Incomum",
    "Cristal da Alma Sanguinária Épico",
    "Cristal da Alma Sanguinária Raro",
    "Cristal da Alma Sanguinária Incomum"
]

FRAGMENTOS_NOMES = [
    "Fragmento Etéreo Épico",
    "Fragmento Etéreo Raro",
    "Fragmento Etéreo Incomum",
    "Fragmento Lunar Épico",
    "Fragmento Lunar Raro",
    "Fragmento Lunar Incomum",
    "Fragmento Solar Épico",
    "Fragmento Solar Raro",
    "Fragmento Solar Incomum",
    "Fragmento Sem Limites Épico",
    "Fragmento Sem Limites Raro",
    "Fragmento Sem Limites Incomum"
]

# Lista de palavras que automaticamente excluem itens
# ==================== LISTA DE ITENS NÃO COMERCIALIZÁVEIS ====================
# Itens que devem ser excluídos da exibição no inventário de comércio
EXCLUIR_PALAVRAS = [
    # === MATERIAIS E CONSUMÍVEIS ===
    "Óleo de Flor", "Pedaço de", "Livro de", "Marca de", "Cristal", "Bastão d",
    "Token de", "Token do", "Panax de", "Grande Pílula", "Pequena Pílula",
    "Esfera da", "Flor de Romã", "Estátua de Dragão", "Erva do Espírito",
    "Selo de Dominação", "Cetro Majestoso", "Fruta Centenária", "Óleo Sagrado",
    "Vela Aromática", "Pedaço do Dragão", "Crachá de",
    "Baleia", "Seda dos", "Japamala", "Anel de Feitiço de Yullus", "Grilheta de",
    "Talismã do", "Crachá de Invocação", "P.E de E.T", "Crachá", "Pedra do Equilíbrio",
    "Pedra Sanguissedenta", "Pedra da Lua Amarela", "Pedra Lúcida Azul",
    "Minério de Chifre", "Pó de espaço", "Espada de Pedras",
    "Pinheiro Resistente", "Gema de Espírito", "Tintura Vermelha", "Token Infundido",
    "Pílula de Gelo", "Pedra do Trovão", "Masse de Enxofre", "Escama de Rainha",
    "Pedra Mágica da Insanidade", "Pergaminho de",
    
    # === MATERIAIS ADICIONAIS (cliente) ===
    "Tenacidade", "Crachá da", "Selo do Trovão", "Berrante de", "Selo de", "Selo da",
    "Froaç Vital", "Bem de Valor", "Lingote", "Bandana", "Pó Ilusório",
    "Lasca", "Essência de Selvagem", "Veneno de Rainha", "Sangue de Nefariox",
    "Estela de", "Casco do", "Pedra da Energia", "Energia do Vazio", "Ornamento",
    "Pó Impecável", "Ser Consciente", "Pedaço da Ombreira", "Coração de Tatu",
    "Sino da", "Reidouro", "Lagrima do Dragão", "Tocha de", "P.E", "Pílula da Grande",
    "Pó de Espaço-tempo", "Pergaminho do Demônio", "Força Vital Esvaída",
    "Pedra Amarela", "Presa do Lobo", "Presa do Lobo da Lúnula de Sangue",
    "Pedra da Energia Demoníaca", "Essência de Dragão", "Pílula Negra",
    "Placa de Comando da Associação da Refinaria Carmesim", "Pó de Nebulosa",
    "Pó de Espírito", "Jade Crescente do Aprendiz",
    
    # === ESPÍRITOS (NÃO SÃO ITENS DE COMÉRCIO) ===
    "Yobi", "Yobi, o Mensageiro da Primavera",
    "Biyoho", "Biyoho, o Descendente Infernal das Chamas",
    "Sumacheon", "Sumacheon, o Rei Demoníaco do Mar do Norte",
    "Styx", "Styx, o Cavaleiro Fantasma",
    "Infernus", "Infernus, Senhor do Inferno",
    "Popotamus", "Popotamus, o Feiticeiro Hipopótamo",
    "Porquínio", "Porquínio, o Grunhista",
    "Tougon", "Tougon, o Monge Violento",
    "Oroonki", "Oroonki, Esqueleto Coração de Leão",
    "Muumuu", "Muumuu, o Mestre dos Touros",
    "Chacha", "Chacha, o Mestre do Disfarce",
    "Sortitude", "Sortitude, o Gato Sortudo",
    "Candela", "Candela, a Imperatriz Radiante",
    "Bisana", "Bisana, a Borboleta Turquesa",
    "Mir", "Mir, o Dragão Radiante",
    "Woosa", "Woosa, o Sábio do Deserto",
    "Zakhan", "Zakhan, o Assassino Sombrio",
    "Drago Ponta", "Drago Ponta de Sangue",
    "Faísca", "Faísca, a Gema Brilhante",
    "Lala", "Lala, a Fada da Floresta",
    "Khalion", "Khalion, o Grande General",
    "Iluminacão", "Iluminacão, o Mestre da Lanterna",
    "Akka Serenidade", "Akka Serenidade",
    "Besouraleiro", "Besouraleiro Carapaça",
    "Lágrima do Dragão Negro",
    "Raposa de três caudas da Neve", "Raposa de Três Caudas da Neve",
    "Rei Leão Khun",
    "Alma do Dragão Branco", "Alma do Dragão",
    "Energia do Demônio do Vazio",
    "Força Vital do Dragão",
    "Lanterna que Guia Espectros",
    
    # === MAIS ESPÍRITOS (lista completa do cliente) ===
    "Anjo da Morte, o Ceifeiro de Almas",
    "Baleiana, a Beleza Absoluta",
    "Balrog, o Lorde do Fogo",
    "Baratan, a Besta Relâmpago",
    "Brutus, o Senhor dos Oceanos",
    "Cavalo Marinho da Investida Selvagem",
    "Chifre Flamejante, o Diabo de Fogo",
    "Cometa, o Dono dos Chifres Vermelhos",
    "Corojel, o Deus Guerreiro",
    "Cristalidro, o Pavão Branco",
    "Cãomandante", "Cãomandante, o Chefe Canino",
    "Darknyan", "Darknyan, o Ressuscitador",
    "Doggo", "Doggo, o Lobo Vermelho",
    "Dragustar", "Dragustar, o Morcego Vampírico",
    "Florida", "Florida, o Anjo Verdejante",
    "Gargas", "Gargas, o Vigia Verdejante",
    "Grande Sábio Símio", "Grande Sábio Símio, o Rei Macaco",
    "Grifavalo", "Grifavalo, o Garanhão Sombrio",
    "Haeryeong", "Haeryeong, o Felino Místico",
    "Haeryu", "Haeryu, o Elementalista da Cura",
    "Horyong", "Horyong, Pequeno Dragão azul-celeste",
    "Hydra", "Hydra, o Dragão de Três Cabeças",
    "Imperador da Destruição", "Imperador da Destruição, o Demônio Infernal Octogonal",
    "Koiga", "Koiga, Coração de Leão Brutal",
    "Lamparino", "Lamparino, o Mensageiro da Alma",
    "Lucy", "Lucy, dos Olhos Vermelhos",
    "Lulu", "Lulu, a Felina Encantada",
    "Mantata", "Mantata, o Barão Azul",
    "Meditogato", "Meditogato, o Gato Celestial",
    "Mosla", "Mosla, a Serpente Obscura",
    "Nerr", "Nerr, o Demônio de Gelo", "Nerr, o Demônio de Gelo das Trevas",
    "Nyanja", "Nyanja Assassino",
    "Pepo", "Pepo, o Rei das Fadas",
    "Poipoi", "Poipoi, o Dragão da Nuvem Negra",
    "Raryo", "Raryo, o Pequeno Dragão Branco",
    "Reidouro", "Reidouro, o Falcão de Fogo",
    "Ringring", "Ringring, o Verdilhão",
    "Rocki", "Rocki, o Dragonino Rochoso",
    "Roxion", "Roxion, o Dragão Demoníaco",
    "Saltita", "Saltita, o Guru Coelho",
    "Setra", "Setra Radiante",
    "Shaoshao", "Shaoshao, o Maníaco", "Shaoshao, o Maníaco das Gemas",
    "Solari", "Solari, a Raposa Milenar",
    "Sonholeta", "Sonholeta, a Fada Borboleta",
    "Suparna", "Suparna, o Pássaro Dourado",
    "Toril", "Toril, o Dragão Divino do Trovão",
    "Vendavalma", "Vendavalma, o Invocador do Vento",
    "Wooska", "Wooska, Príncipe Herdeiro das Trevas",
    "Zeon", "Zeon, o Dragão do Golpe de Relâmpago",
    "Flordoura", "Flordoura, a Dragoa Fada",
    
    # === ITENS DE MISSÃO E DROPS ===
    "Cartaz de Procurados", "Cartaz de Procurado", "Cartaz de Procurado do Pecador",
    "Lágrima de Ymir", "Pedra Cintamani de Ragnos",
    "Coração de Demônio", "Coração do Demônio Negro da Presa do Javali",
    "Sangue Contaminado", "Bambu Mágico",
    "Codificador do", "Alma Regressa",
    "Diagrama de Criação", "Rancor de Arahan",
    "Jade Lúcido Verde", "Jade Lúcido Roxo", "Jade Lúcido",
    "Espada de Prata Pura",
    "Chifre Vermelho", "Chifre Macio",
    "Tambor de Guerra de Barhar",
    "Pedra Umbra do Paraíso das Espadas", "Energia Assombrada",
    "Incenso do Consolo", "Tesouro Misterioso",
    "Provisão Saqueada Pelo Exército Rebelde",
    "Chifre de Dragão Branco", "Couro de Dragão Branco",
    "Escama de Dragão Branco", "Selo do Dragão Branco",
    "Malícia de Arahan", "Sangue de Demônio do Vazio",
    "Erva Mística", "Arvore de Divindade", "Massa de Enxofre",
    "Escama de Tekano",
    "Coração de Capitão Yeticlops",
    "Erva Espiritual", "Folha de Fruta Milenar",
    "Berrante do Chefe",
    "Tesouro Dourado", "Amuleto do Guerreiro Deturpado",
    "Veneno Fatal da Grande Centopeia", "Erva de Sangue Demoníaco",
    "Madeira Inflexível", "Moca de Goblin", "Olho de Kthul",
    
    # === POÇÕES E TÔNICOS ===
    "Poção de Recuperaçao de HP Imensa", "Poção de Recuperação de HP Imensa",
    "Poção de Recuperação de HP Intensa", "Poção de Recuperação de MP Imensa",
    "Tônico de Gânancia Épico", "Tônico de Prosperidade Épico",
    "Tônico de Progresso Épico", "Tônico de Progresso Lendário",
    "Tônico de Prosperidade Lendário", "Tônico de Cura Épico",
    "Poção de Acerto Épico", "Água Divina Épica",
    "Pílula do Assassino", "Pílula de Nuvem Violenta Lendária", "Pílula Solitária Lendária",
    "Bomba Relâmpago Incandescente",
    
    # === FRAGMENTOS DE PEDRA DE APRIMORAMENTO ===
    "Fragmento de Pedra de Aprimoramento do Dragão Divino Incomum",
    "Fragmento de Pedra de Aprimoramento do Dragão Divino Épico",
    "Fragmento de Pedra de Aprimoramento do Dragão Divino Raro",
    "Fragmento de Pedra de Aprimoramento do Dragão Divino Lendário",
    "Fragmento de Pedra de Aprimoramento de Artefato de Dragão do Dragão Divino Épico",
    "Fragmento de Pedra de Aprimoramento de Artefato de Dragão do Dragão Divino Raro",
    "Fragmento de Pedra de Aprimoramento de Artefato de Dragão do Dragão Divino Lendário",
    "Cetro Majestoso de Dragão Negro Lendário",
    "Pequena Pílula de Yin Lendária",
    "Bastão de Sarmati Divino Incomum",
    "[Celebração do Aniversário de 4 Anos]",
    
    # === ESPÍRITOS LENDÁRIOS E ÉPICOS (inglês) ===
    "Toril, o Dragão Divino do Trovão",
    "Anguirus, o Dragão Negro do Incêndio", "Aouad, o Protetor Antigo",
    "Helon, a Fênix Azul", "Crimson Eye Ramil", "Luz Azul Ramil",
    "Alchupka, a Mãe de Todos os Males", "Xikir, a Serpente do Caos",
    "Moa, a Donzela Enfurecida", "Olhos Carmesim Ramil",
    "Tigre Branco Sura", "Sura do Tigre de Fogo", "Gumiho Sura",
    "Vermelho Phurba", "Azul Phurba", "Rei Dragão do Deserto",
    "Rei Dragão do Gelo", "Cavaleiro do Fim, Feruz", "Imperador Demônio",
    "Imperador Orc", "Bao Long, o Alquimista Divino", "Mestre Laguz",
    "General de Gelo do Abismo", "Espírito do Vulcão do Abismo",
    "Devorador de Almas, Nhamund", "Rei Demônio Nagas",
    "Imperador Demônio Nagas", "Imperatriz Milenar", "General Guerreiro Milenar",
    "Dragão Fantasma Sura", "Flor Genseng", "Flor Genseng Negra", "Tigre Branco",
    "White Tiger Sura", "Tigre de Fogo Sura", "Fire Tiger Sura",
    "Fox Spirit Sura", "Espírito de Raposa Sura", "Red Phurba", "Blue Phurba",
    "Cavaleiro Azul Estigma", "Cavaleiro Vermelho Estigma", "Guerreiro Estigma Vermelho",
    "Desert Dragon King", "Ice Dragon King", "Feruz, Knight of the End",
    "Great Demon Emperor", "Imperador dos Orcs", "Great Orc Emperor",
    "Bao Long, a Divine Alchemist", "Master Laguz", "Soul Devourer, Nhamund",
    "Demon King Nagas", "Demonic Emperor Nagas", "Ghost Dragon Sura",
    "Frost General of the Abyss", "Volcano Spirit of the Abyss",
    "Millennial Empress", "Millennial War General",
    
    # === GENÉRICOS (padrões que capturam muitos itens) ===
    "Fragmento de Espaço", "Fragmento de Tempo", "Fragmento de Alma",
    "Essência de", "Pó de", "Poção de", "Elixir de",
    "Bilhete de", "Entrada de", "Convite de", "Ticket de",
    "Missão de", "Quest de", "Tarefa de",
    "Caixa de", "Baú de", "Cofre de", "Pacote de",
    "Ingrediente de", "Material de", "Componente de",
    "Moeda de", "Ficha de", "Emblema de"
]

# ==================== LISTA FIXA DE STATUS PARA FILTROS ====================
# Nomes exatos da API MIR4 (languageCode=pt) - Extraídos diretamente da API
TODOS_STATUS_FILTROS = [
    # === ATRIBUTOS BASE ===
    "HP",
    "MP",
    "Vida",
    "REGENERAÇÃO DE % DE HP (cada 10s)",
    "REGENERAÇÃO DE % DE MP (cada 10s)",
    "ATAQUE FÍSICO",
    "ATAQUE de feitiço",
    "DEFESA FÍSICA",
    "DEFESA contra feitiços",
    "Precisão",
    "EVASÃO",
    "CRÍTICO",
    "EVASÃO DE CRÍTICO",
    
    # === DANO DE ATAQUE ===
    "Aumento do DANO DE ATAQUE CRÍTICO",
    "Aumento do DANO DE ATAQUE de Esmagamento",
    "Aumento do DANO DE ATAQUE em PvP",
    "Aumento do DANO DE ATAQUE de Monstros",
    "Aumento de DANO DE ATAQUE do Boss",
    "Aumento de DANO DE ATAQUE de Habilidade",
    "Aumento de Todo o DANO DE ATAQUE",
    "Aumento do DANO DE ATAQUE Básico",
    
    # === REDUÇÃO DE DANO ===
    "Redução do DANO CRÍTICO Recebido",
    "Redução do DANO de Esmagamento Recebido",
    "Redução do DANO em PvP Recebido",
    "Redução do DANO Recebido de Monstros",
    "Redução do DANO Recebido do Boss",
    "Redução do DANO de Habilidade Recebido",
    "Redução de Todo o DANO Recebido",
    "Redução do DANO DE ATAQUE Básico Recebido",
    
    # === CC E RESISTÊNCIA ===
    "Aumento da Probabilidade de Sucesso de Atordoar",
    "Aumento de RESISTÊNCIA a Atordoar",
    "Aumento da Probabilidade de Sucesso de Debilitação",
    "Aumento de RESISTÊNCIA à Debilitação",
    "Aumento da Probabilidade de Sucesso de Silenciar",
    "Aumento de RESISTÊNCIA a Silenciar",
    "Aumento da Probabilidade de Sucesso de Derrubar",
    "Aumento de RESISTÊNCIA a Derrubar",
    
    # === FARM E EXP ===
    "Aumento de EXP de Caça",
    "Aumento de Ganho de Cobre de Caça",
    "Aumento de Ganho de Energia",
    "Aumento de Ganho de Aço Negro",
    "Aumento da Probabilidade de Obtenção",
    "Aumento da Probabilidade de Obtenção de Sorte",
    
    # === MINERAÇÃO E RECOLHA ===
    "Aceleramento de Tempo de Mineração",
    "Aceleramento do Tempo de Recolha",
    "Aceleramento do Tempo de Recolha de Energia",
    "Aceleramento do Tempo de Abertura de Caixa",
    
    # === PODER ESPECIAL ===
    "Poder Antidemônio",
    "Aumento de Precisão em Monstros",
    "Aumento de EVASÃO de Monstros",
    
    # === COOLDOWN E CUSTO ===
    "Redução do Cooldown de Habilidade",
    "Redução do Custo de MP",
    "Redução do Cooldown de Água Divina",
    
    # === POÇÕES E RECUPERAÇÃO ===
    "Aumento do Efeito da Poção de HP",
    "Aumento do Efeito da Poção de MP",
    "Aumento de Quantidade de Recuperação de HP de Habilidade",
    
    # === VIGOR ===
    "Aumento de Vigor Máximo (segundos)",
    
    # === TREINO ===
    "Aumento da Probabilidade no Sucesso de Treino Ermo",
    
    # === APRIMORAMENTO DE EQUIPAMENTO ===
    "Aumento da Chance de Sucesso do Aprimoramento de Equipamento (Incomum)",
    "Aumento da Chance de Sucesso do Aprimoramento de Equipamento (Raro)",
    "Aumento da Chance de Sucesso do Aprimoramento de Equipamento (Épico)",
    "Aumento da Chance de Sucesso do Aprimoramento de Equipamento (Lendário)",
    "Aumento da Chance de Sucesso do Aprimoramento de Equipamento (de Incomum até Lendário)",
    
    # === APRIMORAMENTO DE ARTEFATO DE DRAGÃO ===
    "Aumento da Chance de Sucesso do Aprimoramento de Artefato de Dragão (Raro)",
    "Aumento da Chance de Sucesso do Aprimoramento de Artefato de Dragão (Épico)",
    "Aumento da Chance de Sucesso do Aprimoramento de Artefato de Dragão (Lendário)",
    "Aumento da Chance de Sucesso do Aprimoramento de Artefato de Dragão (de Incomum até Lendário)",
]
