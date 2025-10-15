from flask import Flask, jsonify, render_template, request
import psycopg2

app = Flask(__name__)
DB_URL = "postgresql://invent_h45i_user:d7jmli6VzlFzM5hldvMiPEOShizgEydt@dpg-d3nuf9emcj7s73f1k84g-a.ohio-postgres.render.com/invent_h45i"

# --- PÁGINAS HTML (FRONTEND) ---
# ... (todo o código anterior continua o mesmo) ...

# --- PÁGINAS HTML (FRONTEND) ---

@app.route('/')
def pagina_inicial():
    return render_template('index.html')

@app.route('/admin')
def pagina_admin():
    return render_template('admin.html')

# MODIFIQUE ESTA ROTA:
@app.route('/inventario/<int:jogador_id>')
def pagina_inventario(jogador_id):
    # Vamos buscar o nome do jogador para exibir no título da página
    jogador_info = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM jogadores WHERE id = %s;", (jogador_id,))
        jogador_db = cur.fetchone()
        cur.close()
        conn.close()
        if jogador_db:
            jogador_info = {'id': jogador_db[0], 'nome': jogador_db[1]}
    except Exception as e:
        print(f"Erro ao buscar jogador: {e}")

    # Renderiza o novo template, passando os dados do jogador
    return render_template('inventario.html', jogador=jogador_info)


# --- ROTAS DA API (BACKEND) ---

# ... (todo o resto do seu código de API continua aqui, sem alterações) ...

# ROTA PARA LISTAR JOGADORES
@app.route('/api/jogadores', methods=['GET'])
def get_jogadores():
    # ... código continua o mesmo
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM jogadores;")
        jogadores_tuplas = cur.fetchall()
        cur.close()
        conn.close()
        lista_de_jogadores = [{'id': tupla[0], 'nome': tupla[1]} for tupla in jogadores_tuplas]
        return jsonify(lista_de_jogadores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOVA ROTA DE API: Listar todos os itens disponíveis no jogo
@app.route('/api/itens', methods=['GET'])
def get_itens():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM itens;")
        itens_tuplas = cur.fetchall()
        cur.close()
        conn.close()
        lista_de_itens = [{'id': tupla[0], 'nome': tupla[1]} for tupla in itens_tuplas]
        return jsonify(lista_de_itens)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOVA ROTA DE API: Adicionar um item ao inventário de um jogador
@app.route('/api/inventario/adicionar', methods=['POST'])
def adicionar_item_inventario():
    dados = request.get_json()
    jogador_id = dados.get('jogador_id')
    item_id = dados.get('item_id')

    if not jogador_id or not item_id:
        return jsonify({'error': 'ID do jogador e do item são obrigatórios.'}), 400
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        sql = "INSERT INTO inventario (jogador_id, item_id) VALUES (%s, %s);"
        cur.execute(sql, (jogador_id, item_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Item adicionado ao inventário com sucesso!'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

# ROTA PARA VER INVENTÁRIO DE UM JOGADOR
@app.route('/api/jogador/<int:jogador_id>/inventario', methods=['GET'])
def get_inventario(jogador_id):
    # ... código continua o mesmo
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = "SELECT itens.nome, itens.descricao, itens.url_imagem FROM inventario JOIN itens ON inventario.item_id = itens.id WHERE inventario.jogador_id = %s;"
        cur.execute(query, (jogador_id,))
        items_do_jogador = cur.fetchall()
        cur.close()
        conn.close()
        inventario_list = [{"nome": item[0], "descricao": item[1], "url_imagem": item[2]} for item in items_do_jogador]
        return jsonify(inventario_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)