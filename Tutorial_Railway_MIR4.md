# 🚂 Tutorial Railway - MIR4 You

## Guia Completo para Gerenciar seu Site

---

## 📋 Índice

1. [Acessando o Railway](#1-acessando-o-railway)
2. [Verificando Status do Site](#2-verificando-status-do-site)
3. [Reiniciando o Site (se cair)](#3-reiniciando-o-site-se-cair)
4. [Vendo os Logs](#4-vendo-os-logs)
5. [Domínio Personalizado](#5-domínio-personalizado)
6. [Variáveis de Ambiente](#6-variáveis-de-ambiente)
7. [Problemas Comuns e Soluções](#7-problemas-comuns-e-soluções)

---

## 1. Acessando o Railway

### Passo a Passo:

1. Acesse: **https://railway.app**
2. Clique em **"Login"** no canto superior direito
3. Faça login com sua conta **GitHub**
4. Você verá o **Dashboard** com seus projetos

### Seu Projeto:
- Nome do projeto: **hunter** (ou similar)
- Serviço: **web** (Flask/Python)

---

## 2. Verificando Status do Site

### No Dashboard:

1. Clique no seu projeto **hunter**
2. Você verá o serviço principal
3. Verifique o **status**:
   - 🟢 **Verde** = Online e funcionando
   - 🟡 **Amarelo** = Deployando/Iniciando
   - 🔴 **Vermelho** = Erro/Offline

### Indicadores Importantes:
- **Uptime**: Tempo que o site está online
- **Memory**: Uso de memória (deve ser < 512MB)
- **CPU**: Uso de processador

---

## 3. Reiniciando o Site (se cair)

### Método 1: Redeploy Manual

1. Acesse seu projeto no Railway
2. Clique no serviço **web**
3. Vá na aba **"Deployments"**
4. Clique nos **3 pontinhos** do último deploy
5. Selecione **"Redeploy"**
6. Aguarde ~2 minutos

### Método 2: Forçar Restart

1. Vá em **Settings** do serviço
2. Role até **"Service"**
3. Clique em **"Restart"**

### Método 3: Via GitHub (recomendado)

1. Faça qualquer alteração mínima no código
2. Faça commit e push
3. O Railway fará deploy automático

---

## 4. Vendo os Logs

### Para Diagnosticar Problemas:

1. Clique no seu serviço
2. Vá na aba **"Logs"**
3. Você verá em tempo real o que acontece

### O que procurar nos logs:
- ✅ `[APP] Sistema de auto-renovação iniciado` = Tudo OK
- ⚠️ `[ERRO]` = Algum problema
- ❌ `Error` ou `Exception` = Erro crítico

### Filtrar Logs:
- Use a barra de busca para filtrar
- Exemplo: digite "ERRO" para ver só erros

---

## 5. Domínio Personalizado

### Seu domínio: mir4you.com

### Se o domínio parar de funcionar:

1. Vá em **Settings** → **Networking**
2. Verifique se o domínio está listado
3. O DNS deve apontar para:
   - **CNAME**: `fshbojur.up.railway.app`

### Verificar DNS:
- Acesse: https://dnschecker.org
- Digite: mir4you.com
- Verifique se aponta para Railway

---

## 6. Variáveis de Ambiente

### Acessando:

1. Clique no serviço
2. Vá em **"Variables"**

### Variáveis Importantes:
```
SECRET_KEY = (chave secreta do Flask)
PORT = (porta do servidor)
```

### ⚠️ CUIDADO:
- Não delete variáveis sem saber o que fazem
- Alterações reiniciam o serviço

---

## 7. Problemas Comuns e Soluções

### ❌ Site não carrega (erro 502/503)

**Causa:** Servidor caiu ou está reiniciando

**Solução:**
1. Vá em Deployments
2. Clique em Redeploy
3. Aguarde 2-3 minutos

---

### ❌ Site muito lento

**Causa:** Cache não carregado

**Solução:**
1. Acesse: https://mir4you.com/reset-cache
2. Clique em "Carregar Cache" no site
3. Aguarde carregar 100%

---

### ❌ Erro ao fazer login

**Causa:** Banco de dados com problema

**Solução:**
1. Acesse: https://mir4you.com/admin
2. Use as novas credenciais:
   - Login: jeannunes7879587
   - Senha: G4@45&*)#1294!@@@$

---

### ❌ Deploy falhou

**Causa:** Erro no código ou dependências

**Solução:**
1. Vá em Deployments
2. Clique no deploy com erro
3. Veja os logs para entender o problema
4. Corrija no GitHub e faça novo push

---

## 📱 URLs Importantes

| Função | URL |
|--------|-----|
| Site Principal | https://mir4you.com |
| Painel Admin | https://mir4you.com/admin |
| Limpar Cache | https://mir4you.com/limpar-cache |
| Reset Cache | https://mir4you.com/reset-cache |
| Status Cache | https://mir4you.com/status-carregamento |
| Railway Dashboard | https://railway.app/dashboard |

---

## 🔧 Comandos Úteis (se precisar)

### Verificar se site está online:
Acesse: https://mir4you.com

### Forçar limpeza de cache:
Acesse: https://mir4you.com/reset-cache

### Ver status do carregamento:
Acesse: https://mir4you.com/status-carregamento

---

## 📞 Suporte

Se tiver problemas que não conseguir resolver:

1. **Tire print** da tela de erro
2. **Copie os logs** do Railway
3. Entre em contato com o desenvolvedor

---

## ✅ Checklist Diário (Opcional)

- [ ] Site está acessível?
- [ ] Login funciona?
- [ ] Cache está carregado?
- [ ] Buscas retornam resultados?

---

**Última atualização:** Janeiro 2026

**Desenvolvido por:** Gabriel Barreto
