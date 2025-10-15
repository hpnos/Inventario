# Arquivo: app.py (versão atualizada)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import database as db

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
ADMIN_PASSWORD = 'ravelgay'

# ... (rotas /, /login, /logout continuam as mesmas) ...
# ... (rota /admin continua a mesma) ...

# --- NOVA ROTA PARA GERENCIAR O CATÁLOGO DE ITENS ---
@app.route('/admin/itens', methods=['GET', 'POST'])
def admin_itens():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Adicionar novo item mestre
        nome = request.form['nome']
        descricao = request.form['descricao']
        imagem_url = request.form['imagem_url']
        if nome and imagem_url:
            db.adicionar_item_mestre(nome, descricao, imagem_url)
        return redirect(url_for('admin_itens'))

    # Listar itens existentes
    itens_mestre = db.listar_itens_mestre()
    return render_template('admin_itens.html', itens=itens_mestre)

# --- ROTA DE GERENCIAR JOGADOR ATUALIZADA ---
@app.route('/jogador/<int:jogador_id>', methods=['GET', 'POST'])
def gerenciar_jogador(jogador_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Adicionar item do catálogo ao inventário do jogador
        item_mestre_id = request.form['item_mestre_id']
        quantidade = request.form['quantidade']
        if item_mestre_id and quantidade:
            db.adicionar_item_ao_inventario(jogador_id, int(item_mestre_id), int(quantidade))
        return redirect(url_for('gerenciar_jogador', jogador_id=jogador_id))

    nome_do_jogador = db.obter_jogador_por_id(jogador_id)
    inventario_do_jogador = db.listar_itens_por_jogador(jogador_id)
    # Precisamos da lista de todos os itens mestre para popular o dropdown
    itens_mestre_disponiveis = db.listar_itens_mestre()

    if nome_do_jogador is None:
        return redirect(url_for('admin'))
    
    return render_template('jogador.html', 
                           nome=nome_do_jogador, 
                           inventario=inventario_do_jogador,
                           jogador_id=jogador_id,
                           itens_mestre=itens_mestre_disponiveis) # Passa a lista para o template

if __name__ == '__main__':
    app.run(debug=True)