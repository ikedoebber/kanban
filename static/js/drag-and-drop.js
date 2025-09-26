// static/js/drag-and-drop.js - Versão robusta

document.addEventListener('DOMContentLoaded', function () {
    // Aguarda um pouco para garantir que as seções foram carregadas
    setTimeout(inicializarArrastarSoltar, 500);
});

function inicializarArrastarSoltar() {
    console.log('🎯 Inicializando sistema de arrastar e soltar...');
    
    // Verifica se os boards necessários existem
    const quadroTarefas = document.getElementById('tasks-board');
    const quadroMetas = document.getElementById('goals-board');
    
    if (!quadroTarefas && !quadroMetas) {
        console.warn('⚠️ Nenhum quadro encontrado, reagendando inicialização...');
        setTimeout(inicializarArrastarSoltar, 1000);
        return;
    }

    // Seleciona todas as colunas disponíveis
    const colunas = document.querySelectorAll('.task-column, .goal-column');
    
    if (colunas.length === 0) {
        console.warn('⚠️ Nenhuma coluna encontrada');
        return;
    }

    console.log(`📋 Encontradas ${colunas.length} colunas`);

    // Remove event listeners anteriores para evitar duplicação
    colunas.forEach(coluna => {
        const cards = coluna.querySelectorAll('.task-card, .goal-card');
        
        console.log(`  Coluna com ${cards.length} cards`);
        
        cards.forEach(card => {
            // Remove listeners antigos se existirem
            card.removeEventListener('dragstart', lidarComInicioArrasto);
            card.removeEventListener('dragend', lidarComFimArrasto);
            
            // Adiciona novos listeners
            card.setAttribute('draggable', true);
            card.addEventListener('dragstart', lidarComInicioArrasto);
            card.addEventListener('dragend', lidarComFimArrasto);
        });

        // Remove listeners antigos da coluna
        coluna.removeEventListener('dragover', lidarComSobreposicaoArrasto);
        coluna.removeEventListener('dragenter', lidarComEntradaArrasto);
        coluna.removeEventListener('dragleave', lidarComSaidaArrasto);
        coluna.removeEventListener('drop', lidarComSoltar);
        
        // Adiciona novos listeners da coluna
        coluna.addEventListener('dragover', lidarComSobreposicaoArrasto);
        coluna.addEventListener('dragenter', lidarComEntradaArrasto);
        coluna.addEventListener('dragleave', lidarComSaidaArrasto);
        coluna.addEventListener('drop', lidarComSoltar);
    });

    let cardArrastado = null;
    let atualizacaoPendente = false;
    let colunaOriginal = null; // Para reverter em caso de erro

    function lidarComInicioArrasto(e) {
        cardArrastado = this;
        colunaOriginal = this.parentElement;
        
        setTimeout(() => this.classList.add('arrastando'), 0);
        e.dataTransfer.effectAllowed = 'move';
        
        console.log('🎯 Arrasto iniciado:', {
            cardId: this.dataset.taskId || this.dataset.goalId,
            tipo: this.dataset.taskId ? 'tarefa' : 'meta'
        });
    }

    function lidarComFimArrasto() {
        this.classList.remove('arrastando');
        cardArrastado = null;
        colunaOriginal = null;
    }

    function lidarComSobreposicaoArrasto(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    function lidarComEntradaArrasto(e) {
        e.preventDefault();
        this.classList.add('sobre-arrasto');
    }

    function lidarComSaidaArrasto() {
        this.classList.remove('sobre-arrasto');
    }

    function lidarComSoltar(e) {
        e.preventDefault();
        this.classList.remove('sobre-arrasto');

        if (atualizacaoPendente) {
            console.warn('⚠️ Operação em andamento, ignorando soltar');
            return;
        }

        const colunaDestino = this;
        const colunaOrigem = cardArrastado?.parentElement.closest('.task-column, .goal-column');

        if (cardArrastado && colunaDestino !== colunaOrigem) {
            atualizacaoPendente = true;
            
            console.log('📦 Soltar executado:', {
                origem: colunaOrigem?.classList.toString(),
                destino: colunaDestino?.classList.toString()
            });
            
            mostrarIndicadorCarregamento(cardArrastado);

            // Move o card temporariamente para feedback visual imediato
            const conteudoColuna = colunaDestino.querySelector('.column-content');
            if (conteudoColuna) {
                conteudoColuna.appendChild(cardArrastado);
            }

            const idTarefa = cardArrastado.dataset.taskId;
            const idMeta = cardArrastado.dataset.goalId;

            if (idTarefa) {
                const novoStatus = obterStatusTarefaDaColuna(colunaDestino);
                console.log(`📋 Atualizando tarefa ${idTarefa} para status: ${novoStatus}`);
                atualizarStatusItem(idTarefa, novoStatus, 'tarefa');
            } else if (idMeta) {
                const novoPeriodo = obterPeriodoMetaDaColuna(colunaDestino);
                console.log(`🎯 Atualizando meta ${idMeta} para período: ${novoPeriodo}`);
                atualizarPeriodoMeta(idMeta, novoPeriodo, 'meta');
            } else {
                console.error('❌ Card sem ID válido');
                atualizacaoPendente = false;
                ocultarIndicadorCarregamento(cardArrastado);
            }
        }
    }

    function mostrarIndicadorCarregamento(card) {
        if (!card) return;
        
        card.style.opacity = '0.6';
        card.style.pointerEvents = 'none';
        
        if (!card.querySelector('.loading-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.innerHTML = '⏳';
            spinner.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 16px;
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            card.style.position = 'relative';
            card.appendChild(spinner);
        }
    }

    function ocultarIndicadorCarregamento(card) {
        if (card) {
            card.style.opacity = '';
            card.style.pointerEvents = '';
            const spinner = card.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }
    }

    function reverterPosicaoCard(card) {
        if (card && colunaOriginal) {
            console.log('↩️ Revertendo posição do card');
            colunaOriginal.appendChild(card);
        }
    }

    function obterStatusTarefaDaColuna(colunaElemento) {
        const classList = colunaElemento.classList;
        if (classList.contains('todo')) return 'todo';
        if (classList.contains('in-progress')) return 'in_progress';
        if (classList.contains('done')) return 'done';
        return null;
    }

    function obterPeriodoMetaDaColuna(colunaElemento) {
        const classList = colunaElemento.classList;
        if (classList.contains('weekly')) return 'weekly';
        if (classList.contains('monthly')) return 'monthly';
        if (classList.contains('quarterly')) return 'quarterly';
        if (classList.contains('biannual')) return 'biannual';
        if (classList.contains('annual')) return 'annual';
        return null;
    }

    function atualizarStatusItem(itemId, novoStatus, tipoItem) {
        console.log('📡 Enviando atualização:', { itemId, novoStatus, tipoItem });

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            console.error('❌ Token CSRF não encontrado');
            lidarComErroAtualizacao('Token CSRF não encontrado');
            return;
        }

        let url;
        if (tipoItem === 'tarefa') {
            url = '/tasks/update-status/';
        } else {
            console.error('❌ Tipo de item não suportado:', tipoItem);
            lidarComErroAtualizacao('Tipo de item não suportado');
            return;
        }

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                id: parseInt(itemId),
                status: novoStatus
            })
        })
        .then(response => {
            console.log('📡 Resposta recebida:', response.status);
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Dados recebidos:', data);
            
            if (data.success) {
                console.log('✅ Status atualizado com sucesso!');
                lidarComSucessoAtualizacao('tarefas');
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao atualizar status:', error);
            lidarComErroAtualizacao(error.message);
        });
    }

    function atualizarPeriodoMeta(metaId, novoPeriodo, tipoItem) {
        console.log('📡 Enviando atualização de período:', { metaId, novoPeriodo, tipoItem });

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            console.error('❌ Token CSRF não encontrado');
            lidarComErroAtualizacao('Token CSRF não encontrado');
            return;
        }

        let url;
        if (tipoItem === 'meta') {
            url = '/goals/update-period/';
        } else {
            console.error('❌ Tipo de item não suportado:', tipoItem);
            lidarComErroAtualizacao('Tipo de item não suportado');
            return;
        }

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                id: parseInt(metaId),
                period: novoPeriodo
            })
        })
        .then(response => {
            console.log('📡 Resposta recebida:', response.status);
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Dados recebidos:', data);
            
            if (data.success) {
                console.log('✅ Período atualizado com sucesso!');
                lidarComSucessoAtualizacao('metas');
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao atualizar período:', error);
            lidarComErroAtualizacao(error.message);
        });
    }

    function lidarComSucessoAtualizacao(secao) {
        setTimeout(() => {
            if (typeof refreshSection === 'function') {
                console.log(`🔄 Atualizando seção ${secao}`);
                refreshSection(secao);
            } else {
                console.log('🔄 Alternativa: recarregando página');
                location.reload();
            }
            atualizacaoPendente = false;
        }, 300);
    }

    function lidarComErroAtualizacao(mensagemErro) {
        alert(`Erro: ${mensagemErro}\nTente novamente.`);
        
        // Reverte posição do card
        reverterPosicaoCard(cardArrastado);
        ocultarIndicadorCarregamento(cardArrastado);
        atualizacaoPendente = false;
    }
}

// Exporta função para uso global
window.inicializarArrastarSoltar = inicializarArrastarSoltar;