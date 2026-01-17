// static/js/pedras.js

// Função para mostrar detalhes da pedra
function mostrarDetalhesPedra(uid, nome, imagem, status) {
    const modal = document.getElementById('pedra-modal');
    const statusTable = document.getElementById('modal-pedra-status');
    const semStatus = document.getElementById('modal-sem-status');
    
    // Limpar tabela anterior
    statusTable.innerHTML = '';
    
    // Preencher informações básicas
    document.getElementById('modal-pedra-img').src = imagem;
    document.getElementById('modal-pedra-nome').textContent = nome;
    document.getElementById('modal-pedra-uid').textContent = `UID: ${uid.substring(0, 8)}...`;
    
    // Extrair tier do nome
    const tierMatch = nome.match(/Tier\s*(\d+)/i) || nome.match(/[Tt](\d+)/);
    document.getElementById('modal-pedra-tier').textContent = tierMatch ? `Tier ${tierMatch[1]}` : 'Tier 1';
    
    // Extrair enhance
    const enhanceMatch = nome.match(/\+(\d+)/);
    const enhanceElem = document.getElementById('modal-pedra-enhance');
    if (enhanceMatch) {
        enhanceElem.textContent = `+${enhanceMatch[1]}`;
        enhanceElem.style.display = 'inline-block';
    } else {
        enhanceElem.style.display = 'none';
    }
    
    // Preencher status
    if (status && status.length > 0) {
        statusTable.style.display = 'table';
        semStatus.style.display = 'none';
        
        status.forEach(stat => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${stat.nome}</td>
                <td>${stat.valor}</td>
            `;
            statusTable.appendChild(row);
        });
    } else {
        statusTable.style.display = 'none';
        semStatus.style.display = 'block';
    }
    
    // Mostrar modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Função para fechar modal
function fecharModalPedra() {
    const modal = document.getElementById('pedra-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Fechar modal ao clicar fora
    const modal = document.getElementById('pedra-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                fecharModalPedra();
            }
        });
    }
    
    // Fechar com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharModalPedra();
        }
    });
    
    // Botão de fechar do modal
    const closeBtn = document.querySelector('.modal-close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', fecharModalPedra);
    }
    
    // Botão de ação do modal
    const actionBtn = document.querySelector('.modal-action-btn');
    if (actionBtn) {
        actionBtn.addEventListener('click', fecharModalPedra);
    }
});