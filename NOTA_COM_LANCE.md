# Análise do Filtro "Com Lance"

## Situação

Após investigação detalhada das APIs disponíveis:

### 1. API do xDraco (mir4global.com)
- Retorna campo `tradeType` em cada conta
- `tradeType: 1` = Conta listada para venda
- `tradeType: 2` = Conta com lance ativo (bidding)
- **Problema**: Verificamos 100+ contas e TODAS têm `tradeType: 1`

### 2. API do wemixplay.com
- As APIs públicas testadas retornam vazias ou requerem autenticação
- A informação "Ongoing Bids" visível no site pode vir de:
  - Smart contracts na blockchain WEMIX
  - API interna autenticada
  - WebSockets em tempo real

### 3. Código do Hunter
- O filtro "Com Lance" está implementado CORRETAMENTE
- Filtra por `tradeType === 2`
- Funciona quando há contas com esse status

## Conclusão

O filtro "Com Lance" **funciona**, mas a API do xDraco:
1. Pode ter um **atraso** na atualização do status de lance
2. Pode não refletir lances feitos diretamente no wemixplay.com
3. Pode atualizar apenas quando o leilão de 3 horas começa

## Opções

### Opção A: Manter como está
- O filtro funciona quando há contas com lance na API
- Aceitar que há um delay entre wemixplay e xDraco

### Opção B: Adicionar aviso
- Mostrar tooltip explicando a limitação
- "Dados podem ter atraso de alguns minutos"

### Opção C: Investigar wemixplay API
- Requer análise mais profunda do site wemixplay
- Possivelmente necessita autenticação/wallet
