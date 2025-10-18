// Seletores de Elementos (Adicionamos os novos seletores do painel de ícones)
const formAddJogador = document.getElementById('form-add-jogador');
const nomeInput = document.getElementById('nome-jogador');
const selectJogador = document.getElementById('select-jogador');
const selectItem = document.getElementById('select-item');
const formAddItem = document.getElementById('form-add-item');
const listaInventario = document.getElementById('lista-inventario-jogador');
const formGrantIcon = document.getElementById('form-grant-icon');
const selectJogadorIcon = document.getElementById('select-jogador-icon');
const selectIcon = document.getElementById('select-icon');

// Funções
function mostrarInventario(jogadorId) {
    listaInventario.innerHTML = '<li>Carregando...</li>';
    if (!jogadorId) {
        listaInventario.innerHTML = '<li>Selecione um jogador para ver o inventário.</li>';
        return;
    }
    fetch(`/api/jogador/${jogadorId}/inventario`).then(res => res.json()).then(inventario => {
        listaInventario.innerHTML = '';
        if (inventario.length === 0) {
            listaInventario.innerHTML = '<li>Este inventário está vazio.</li>';
        } else {
            inventario.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span>${item.nome}</span> <button class="remove-btn" data-inventario-id="${item.inventario_id}">Remover</button>`;
                listaInventario.appendChild(li);
            });
        }
    });
}

function carregarJogadores() {
    fetch('/api/jogadores').then(res => res.json()).then(jogadores => {
        selectJogador.innerHTML = '<option value="">Selecione um Jogador</option>';
        // MODIFICADO: Também popula o dropdown de jogadores no painel de ícones
        selectJogadorIcon.innerHTML = '<option value="">Selecione um Jogador</option>';
        jogadores.forEach(j => {
            const optionHTML = `<option value="${j.id}">${j.nome}</option>`;
            selectJogador.innerHTML += optionHTML;
            selectJogadorIcon.innerHTML += optionHTML;
        });
    });
}

function carregarItens() {
    fetch('/api/itens').then(res => res.json()).then(itens => {
        selectItem.innerHTML = '<option value="">Selecione um Item</option>';
        itens.forEach(i => {
            selectItem.innerHTML += `<option value="${i.id}">${i.nome}</option>`;
        });
    });
}

// NOVA FUNÇÃO: Busca os ícones disponíveis na API e preenche o dropdown
function carregarIconesDisponiveis() {
    fetch('/api/icons')
        .then(res => res.json())
        .then(icons => {
            // Adiciona uma opção padrão para remover o ícone existente
            selectIcon.innerHTML = '<option value="">Remover Ícone</option>';
            icons.forEach(iconUrl => {
                const iconName = iconUrl.split('/').pop(); // Extrai apenas o nome do arquivo da URL
                selectIcon.innerHTML += `<option value="${iconUrl}">${iconName}</option>`;
            });
        });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    carregarJogadores();
    carregarItens();
    // MODIFICADO: Chama a nova função para carregar os ícones quando a página abre
    carregarIconesDisponiveis();
    mostrarInventario(null);
});

selectJogador.addEventListener('change', (e) => mostrarInventario(e.target.value));

formAddJogador.addEventListener('submit', (event) => {
    event.preventDefault();
    fetch('/api/jogador', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nome: nomeInput.value }) })
    .then(res => res.json()).then(data => { 
        alert(data.message || data.error); 
        nomeInput.value = ''; 
        carregarJogadores(); 
    });
});

formAddItem.addEventListener('submit', (event) => {
    event.preventDefault();
    fetch('/api/inventario/adicionar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jogador_id: selectJogador.value, item_id: selectItem.value }) })
    .then(res => res.json()).then(data => { 
        alert(data.message || data.error); 
        mostrarInventario(selectJogador.value); 
    });
});

listaInventario.addEventListener('click', (event) => {
    if (event.target && event.target.classList.contains('remove-btn')) {
        const inventarioId = event.target.dataset.inventarioId;
        if (confirm('Tem certeza que deseja remover este item?')) {
            fetch(`/api/inventario/remover/${inventarioId}`, { method: 'DELETE' }).then(res => res.json()).then(data => {
                alert(data.message || data.error);
                mostrarInventario(selectJogador.value);
            });
        }
    }
});

// NOVO EVENT LISTENER: Controla o envio do formulário de conceder ícones
formGrantIcon.addEventListener('submit', (event) => {
    event.preventDefault();
    const jogadorId = selectJogadorIcon.value;
    const iconUrl = selectIcon.value;

    if (!jogadorId) {
        alert('Por favor, selecione um jogador.');
        return;
    }

    fetch('/api/jogador/definir-icone', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jogador_id: jogadorId, icon_url: iconUrl })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
    });
});