import requests
import json

# 🔹 Defina manualmente o transportID de uma conta válida
transport_id = 324582  # substitua pelo valor da sua conta

# 🔹 Chamada da API de espíritos
res_spirits = requests.get(f"https://webapi.mir4global.com/nft/character/spirit?transportID={transport_id}&languageCode=pt")
data_spirits = res_spirits.json()

# 🔍 Ver conteúdo bruto da resposta
print("📦 JSON completo dos espíritos:")
print(json.dumps(data_spirits, indent=2, ensure_ascii=False))

# Pegando a lista de espíritos
espiritos_data = data_spirits.get("data", {}).get("spiritList", [])

# 🔍 Ver a lista original
print("\n🌀 Lista de espíritos recebida:")
print(espiritos_data)

# 🔹 Cores por raridade
raridades = {
    "5": "dourado",
    "4": "vermelho",
    "3": "azul",
    "2": "verde",
    "1": "cinza"
}

# Formatando
espiritos_formatados = []
for spirit in espiritos_data:
    grade = spirit.get("grade", "1")
    cor = raridades.get(grade, "cinza")
    espiritos_formatados.append({
        "petName": spirit.get("petName", "Sem Nome"),
        "petOrigin": spirit.get("petOrigin", ""),
        "iconPath": spirit.get("iconPath", ""),
        "cor": cor
    })

# 🔍 Ver os espíritos prontos pra exibir no site
print("\n✅ Espíritos formatados prontos pra exibir no HTML:")
for e in espiritos_formatados:
    print(e)
