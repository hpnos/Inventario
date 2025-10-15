// A constante jogadorId precisa ser definida no HTML antes de chamar este script.
// Veja o passo 4.

const inventarioGrid = document.getElementById('inventario-grid');

// Busca os dados do inventário na nossa API
fetch(`/api/jogador/${jogadorId}/inventario`)
    .then(response => response.json())
    .then(itens => {
        if (itens.length === 0) {
            inventarioGrid.innerHTML = '<p style="color: #3a2d1c;">Este inventário está vazio.</p>';
            return;
        }

        // Para cada item, cria um slot com a imagem e o tooltip
        itens.forEach(item => {
            const slot = document.createElement('div');
            slot.className = 'item-slot';

            slot.innerHTML = `
                <img src="${item.url_imagem}" alt="${item.nome}">
                <div class="tooltip">
                    <h3>${item.nome}</h3>
                    <p>${item.descricao}</p>
                </div>
            `;
            inventarioGrid.appendChild(slot);
        });
    })
    .catch(error => {
        console.error('Erro ao carregar inventário:', error);
        inventarioGrid.innerHTML = '<p>Não foi possível carregar o inventário.</p>';
    });