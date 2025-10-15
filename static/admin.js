// Seletores de Elementos
const formAddJogador = document.getElementById('form-add-jogador');
const nomeInput = document.getElementById('nome-jogador'); // Agora o input já existe no HTML

const selectJogador = document.getElementById('select-jogador');
const selectItem = document.getElementById('select-item');
const formAddItem = document.getElementById('form-add-item');
const listaInventario = document.getElementById('lista-inventario-jogador');

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
        jogadores.forEach(j => {
            selectJogador.innerHTML += `<option value="${j.id}">${j.nome}</option>`;
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

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    carregarJogadores();
    carregarItens();
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