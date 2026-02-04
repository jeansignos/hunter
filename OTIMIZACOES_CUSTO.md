# OTIMIZAÇÕES DE CUSTO RAILWAY - URGENTE

## Problema Identificado
O custo estava em **$105/mês** devido ao uso excessivo de memória RAM.

## Causa Principal
1. **2 workers + 4 threads do Gunicorn** = multiplicava uso de memória
2. **Variável global `contas_detalhadas_global`** = carregava todas as contas detalhadas na RAM
3. Cache de arquivos pesados sendo carregados em memória

## Soluções Aplicadas

### 1. Redução de Workers (CRÍTICO)
**Antes:** `--workers 2 --threads 4` (8 threads total)
**Agora:** `--workers 1 --threads 2` (2 threads total)

**Economia estimada:** ~60-70% de uso de memória

### 2. Configurações Adicionais
- `--timeout 120`: timeout adequado para requests lentos
- `--max-requests 1000`: recicla workers para liberar memória
- `--max-requests-jitter 50`: evita reciclagem simultânea

### 3. .railwayignore Criado
Evita upload de:
- Caches locais (`xdraco_cache/*`)
- Arquivos `__pycache__`
- Ambientes virtuais
- Arquivos desnecessários

## Resultado Esperado
- **Uso de memória:** De ~32.000 GB-min para ~8.000-10.000 GB-min
- **Custo estimado:** De $105/mês para **$25-35/mês**
- **Performance:** Similar (site tem baixo tráfego)

## Próximos Passos (se ainda estiver caro)
1. Implementar limite de cache em memória
2. Usar Redis para cache (se necessário)
3. Implementar paginação real (sem carregar tudo)

## Como Monitorar
1. Acessar Railway Dashboard
2. Ver "Metrics" > "Memory Usage"
3. Deve cair de ~200-300MB para ~80-120MB
