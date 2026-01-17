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
    "2": "feiticeira", 
    "3": "taoista",
    "4": "lanceiro",
    "5": "arqueira",
    "6": "invocador",
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
EXCLUIR_PALAVRAS = [
    "Óleo de Flor", "Pedaço de", "Livro de", "Marca de", "Cristal", "Bastão d",
    "Token de", "Token do", "Panax de", "Grande Pílula", "Pequena Pílula",
    "Esfera da", "Flor de Romã", "Estátua de Dragão", "Erva do Espírito",
    "Selo de Dominação", "Cetro Majestoso", "Fruta Centenária", "Óleo Sagrado",
    "Yobi", "Vela Aromática", "Pedaço do Dragão", "Sumacheon", "Crachá de",
    "Baleia", "Seda dos", "Japamala", "Anel de Feitiço de Yullus", "Grilheta de",
    "Talismã do", "Crachá de Invocação", "P.E de E.T", "Crachá", "Pedra do Equilíbrio",
    "Pedra Sanguissedenta", "Pedra da Lua Amarela", "Pedra Lúcida Azul",
    "Minério de Chifre", "Pó de espaço", "Biyoho", "Espada de Pedras",
    "Pinheiro Resistente", "Gema de Espírito", "Tintura Vermelha", "Token Infundido",
    "Pílula de Gelo", "Pedra do Trovão", "Masse de Enxofre", "Escama de Rainha",
    "Grande Sábio Símio", "Pedra Mágica da Insanidade", "Pergaminho de"
]
