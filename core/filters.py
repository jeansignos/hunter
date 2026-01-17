"""
Funções de filtro e formatação
"""
import re
import unicodedata
import hashlib
from core.constants import EXCLUIR_PALAVRAS, BILHETES_NOMES, CRISTAIS_NOMES, FRAGMENTOS_NOMES


def formatar_valor(valor_str):
    """Converte string de valor para float"""
    if not valor_str:
        return 0
    
    try:
        valor_str = str(valor_str).strip()
        
        if valor_str == '' or valor_str == '-':
            return 0
        
        valor_str = valor_str.replace(',', '').replace('%', '').replace(' ', '')
        valor_str = re.sub(r'[a-zA-Z]+$', '', valor_str)
        
        if valor_str == '':
            return 0
        
        return float(valor_str)
    except Exception as e:
        print(f"Erro ao formatar valor '{valor_str}': {e}")
        return 0


def normalizar_nome_status(nome):
    """Normaliza nome de status para comparação"""
    return unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII').upper()


def hash_status(nome_status):
    """Gera hash curto para identificar status"""
    return hashlib.md5(nome_status.encode()).hexdigest()[:8]


def roman_to_int(roman):
    """Converte número romano para inteiro"""
    if not roman:
        return 1
    
    roman = str(roman).upper().strip()
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    
    if roman.isdigit():
        return int(roman)
    
    total = 0
    prev_value = 0
    
    for char in reversed(roman):
        value = roman_map.get(char, 0)
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    
    return total if total > 0 else 1


def eh_excecao_permitida(nome_item):
    """Verifica se o item é uma exceção às regras de exclusão"""
    if nome_item.startswith("Fragmento Iluminante"):
        return True
    if nome_item.startswith("Fragmento de Tesouro Lendário"):
        return True
    if "Pedra Mágica" in nome_item and "Pedra Mágica da Insanidade" not in nome_item:
        return True
    if "Pedra de Aprimoramento" in nome_item:
        return True
    if "Colar de Ragnos Raro" in nome_item:
        return True
    if nome_item == "Pergaminho de Encantamento":
        return True
    return False


def filtrar_itens_comercializaveis(inventario):
    """
    Filtra itens comercializáveis baseado no quarto dígito do itemID e regras de nome.
    """
    itens_comerciais = []
    
    if not inventario or not isinstance(inventario, list):
        return itens_comerciais
    
    for item in inventario:
        if not isinstance(item, dict):
            continue
            
        item_id = str(item.get("itemID", ""))
        item_name = item.get("itemName", "")
        
        # Exclui itens com "Bilhete" no nome
        if "Bilhete" in item_name:
            continue
            
        # Verifica se é exceção permitida
        if not eh_excecao_permitida(item_name):
            # Verifica exclusões por palavras
            excluir_item = False
            for palavra in EXCLUIR_PALAVRAS:
                if item_name.startswith(palavra):
                    excluir_item = True
                    break
            
            if excluir_item:
                continue
            
            if item_name.startswith("Pedra de") and "Pedra Mágica" not in item_name:
                continue
            
            if item_name.startswith("Fragmento") and "Fragmento Iluminante" not in item_name:
                continue
            
            if item.get("petName"):
                continue
        
        # Verifica se o itemID tem pelo menos 4 dígitos e é tradeável
        if len(item_id) >= 4 and item_id[3] == "1":
            quantidade = item.get("stack", 0) or 1
            grade = int(item.get("grade", "0")) if str(item.get("grade", "0")).isdigit() else 0
            tier = item.get("tier", "I")
            enhance = int(item.get("enhance", 0))
            
            # Define cor de fundo baseado na grade
            cor_fundo = ""
            if grade == 5:
                cor_fundo = "fundo-lendario"
            elif grade == 4:
                cor_fundo = "fundo-epico"
            elif grade == 3:
                cor_fundo = "fundo-raro"
            elif grade == 2:
                cor_fundo = "fundo-incomum"
            elif grade == 1:
                cor_fundo = "fundo-comum"
            
            itens_comerciais.append({
                "nome": item_name,
                "quantidade": quantidade,
                "imagem": item.get("itemPath", ""),
                "grade": grade,
                "tier": tier,
                "enhance": enhance,
                "itemID": item_id,
                "cor_fundo": cor_fundo
            })
    
    # Ordena por grade decrescente
    itens_comerciais.sort(key=lambda x: (-x["grade"], -roman_to_int(x["tier"]), -x["enhance"]))
    
    return itens_comerciais


def filtrar_itens_especiais(inventario):
    """
    Filtra bilhetes, cristais e fragmentos especiais do inventário.
    """
    bilhetes = []
    cristais = []
    fragmentos = []
    
    if not inventario or not isinstance(inventario, list):
        return bilhetes, cristais, fragmentos
    
    PESOS_RARIDADE = {"Épico": 3, "Raro": 2, "Incomum": 1}
    
    for item in inventario:
        if not isinstance(item, dict):
            continue
            
        item_name = item.get("itemName", "")
        stack = int(item.get("stack", 0)) or 1
        
        if item_name in BILHETES_NOMES:
            bilhetes.append({
                "name": item_name,
                "count": stack,
                "img": item.get("itemPath", ""),
                "grade": int(item.get("grade", 1))
            })
        elif item_name in CRISTAIS_NOMES:
            raridade = item_name.split()[-1]
            cristais.append({
                "name": item_name,
                "count": stack,
                "img": item.get("itemPath", ""),
                "grade": int(item.get("grade", 1)),
                "peso_raridade": PESOS_RARIDADE.get(raridade, 0)
            })
        elif item_name in FRAGMENTOS_NOMES:
            raridade = item_name.split()[-1]
            fragmentos.append({
                "name": item_name,
                "count": stack,
                "img": item.get("itemPath", ""),
                "grade": int(item.get("grade", 1)),
                "peso_raridade": PESOS_RARIDADE.get(raridade, 0)
            })
    
    bilhetes.sort(key=lambda x: x["name"])
    cristais.sort(key=lambda x: (-x["peso_raridade"], x["name"]))
    fragmentos.sort(key=lambda x: (-x["peso_raridade"], x["name"]))
    
    # Remove campos de ordenação
    for cristal in cristais:
        cristal.pop("peso_raridade", None)
    for fragmento in fragmentos:
        fragmento.pop("peso_raridade", None)
    
    return bilhetes, cristais, fragmentos


def processar_equipamento_para_frontend(equipamento):
    """Converte equipamento da API para formato do frontend"""
    if not equipamento:
        return None
    
    try:
        return {
            "name": equipamento.get("nome", ""),
            "grade": equipamento.get("grade", 1),
            "tier": roman_to_int(equipamento.get("tier", "I")),
            "enhance": equipamento.get("aprimoramento", 0),
            "count": 1,
            "img": equipamento.get("img", ""),
            "trade": equipamento.get("trade", False),
            "cor_fundo": equipamento.get("cor_fundo", "")
        }
    except Exception as e:
        print(f"Erro ao processar equipamento: {e}")
        return None
