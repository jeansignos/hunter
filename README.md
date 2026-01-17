# MIR4 Market Hunter

Sistema de busca e filtro de contas NFT do jogo MIR4, com sistema de login, Premium e cache otimizado.

## 🚀 Funcionalidades

### Sistema de Login e Premium
- ✅ Registro de usuários
- ✅ Login/Logout com Flask-Login
- ✅ Sistema Premium com expiração de 30 dias
- ✅ Painel administrativo para gestão de usuários
- ✅ Ativação/desativação de Premium pelo admin

### Filtros de Busca
- ✅ Filtro por classe (Guerreiro, Maga, Taoísta, Arqueira, etc.)
- ✅ Filtro por poder e level
- ✅ Filtro por preço em WEMIX
- ✅ Filtro por nível de mina
- ✅ Filtro por Codex
- ✅ Filtro por status de mineração (Boost, Aço Negro)
- ✅ **NOVO** Filtro por itens comercializáveis (2+ itens épicos/lendários)

### Cache Otimizado
- ✅ Cache de contas com TTL configurável
- ✅ Carregamento em background com threading
- ✅ Cache de preço WEMIX/BRL
- ✅ Limpeza automática de cache antigo

### Integrações
- ✅ API xDraco para dados de NFTs
- ✅ CoinMarketCap para conversão WEMIX → BRL

## 📁 Estrutura do Projeto

```
Projeto Jean 2/
├── app.py                 # Aplicação principal Flask
├── config.py              # Configurações (dev/prod/test)
├── models.py              # Modelos SQLAlchemy (User, PremiumActivation)
├── forms.py               # Formulários WTForms
├── requirements.txt       # Dependências Python
├── Procfile              # Deploy Railway
├── railway.json          # Configuração Railway
├── runtime.txt           # Versão Python
├── .env.example          # Exemplo de variáveis de ambiente
├── blueprints/
│   ├── __init__.py
│   ├── auth.py           # Rotas de autenticação
│   └── admin.py          # Rotas administrativas
├── core/
│   ├── __init__.py
│   ├── api.py            # Funções de API xDraco
│   ├── cache.py          # Sistema de cache
│   ├── constants.py      # Constantes e configurações
│   ├── filters.py        # Funções de filtro
│   └── loader.py         # Carregamento de contas
├── templates/
│   ├── index_filtro.html # Página principal
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── admin/
│       ├── dashboard.html
│       └── users.html
└── static/
    ├── style.css
    ├── icons/
    ├── img/
    └── skills/
```

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd "Projeto Jean 2"
```

### 2. Crie o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5001`

## 👤 Acesso Inicial

Após iniciar a aplicação, um usuário admin é criado automaticamente:

- **Email:** admin@mir4market.com
- **Senha:** admin123

⚠️ **IMPORTANTE:** Altere a senha do admin em produção!

## 🚀 Deploy no Railway

### 1. Crie um projeto no Railway
- Acesse [railway.app](https://railway.app)
- Crie um novo projeto

### 2. Configure as variáveis de ambiente
```
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-muito-segura
DATABASE_URL=<será fornecido automaticamente se usar PostgreSQL>
CMC_API_KEY=sua-chave-coinmarketcap
```

### 3. Deploy
O Railway detectará automaticamente o `Procfile` e fará o deploy.

## 🔐 Sistema Premium

### Como funciona
- Usuários podem se registrar gratuitamente
- Admin pode ativar Premium para usuários (30 dias)
- Filtros avançados de status são exclusivos para Premium
- Usuários Premium veem badge especial na interface

### Ativando Premium
1. Acesse `/admin/users` como admin
2. Clique em "Ativar Premium" no usuário desejado
3. O Premium expira automaticamente após 30 dias

## 📝 APIs Utilizadas

### xDraco NFT API
- **Base URL:** `https://webapi.mir4global.com/nft/`
- Endpoints:
  - `/lists` - Lista de contas
  - `/character/summary` - Detalhes da conta
  - `/character/inven` - Inventário
  - `/character/spirit` - Espíritos
  - `/character/skills` - Habilidades

### CoinMarketCap API
- Conversão WEMIX → BRL
- Cache de 5 minutos

## 🐛 Troubleshooting

### Cache não carrega
- Verifique conexão com internet
- Limpe o cache: acesse `/limpar-cache`
- Verifique logs do terminal

### Erro de login
- Verifique se o banco de dados foi criado
- Verifique as variáveis de ambiente

### Erro de API
- Verifique se a API do xDraco está disponível
- Verifique sua chave da CoinMarketCap

## 📜 Licença

Este projeto é privado e de uso exclusivo do cliente.

---

Desenvolvido com ❤️ usando Flask, SQLAlchemy e muito café ☕
