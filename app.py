# 1. IMPORTAÇÕES
# Ferramentas do Flask para criar o app, retornar JSON, renderizar HTML, etc.
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
# Ferramenta para criar o nosso "decorator" de login
from functools import wraps
# Ferramenta para conectar ao banco de dados PostgreSQL
import psycopg2


# 2. CONFIGURAÇÃO INICIAL DO APP
app = Flask(__name__)

# CHAVE SECRETA: Essencial para o sistema de login (sessões) funcionar.
# Troque por qualquer texto aleatório e complexo.
app.secret_key = 'sua-chave-secreta-pode-ser-qualquer-coisa'

# URL DE CONEXÃO: O endereço do seu banco de dados no Render.
DB_URL = "postgresql://invent_h45i_user:d7jmli6VzlFzM5hldvMiPEOShizgEydt@dpg-d3nuf9emcj7s73f1k84g-a.ohio-postgres.render.com/invent_h45i"


# 3. LÓGICA DE AUTENTICAÇÃO

# Decorator que verifica se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            # Se não houver 'logged_in' na sessão, redireciona para a página de login
            return redirect(url_for('pagina_login'))
        return f(*args, **kwargs)
    return decorated_function


# 4. ROTAS QUE RENDERIZAM PÁGINAS HTML (FRONTEND)

# Rota para a página inicial
@app.route('/')
def pagina_inicial():
    return render_template('index.html')

# Rota para a página de admin, agora protegida pelo decorator
@app.route('/admin')
@login_required
def pagina_admin():
    return render_template('admin.html')

# Rota para a página de visualização de inventário de um jogador
@app.route('/inventario/<int:jogador_id>')
def pagina_inventario(jogador_id):
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
    return render_template('inventario.html', jogador=jogador_info)

# Rota para a página de login (aceita GET para mostrar a página, POST para processar o login)
@app.route('/login', methods=['GET', 'POST'])
def pagina_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'Ravel@5858':
            session['logged_in'] = True
            return redirect(url_for('pagina_admin'))
        else:
            error = 'Credenciais inválidas. Tente novamente.'
    return render_template('login.html', error=error)

# Rota para fazer logout (limpar a sessão)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('pagina_login'))


# 5. ROTAS DE API QUE RETORNAM DADOS JSON (BACKEND)
# API para listar todos os jogadores

# API para ver o inventário de um jogador específico
@app.route('/api/jogador/<int:jogador_id>/inventario', methods=['GET'])
def get_inventario(jogador_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = """
            SELECT inventario.id, itens.nome, itens.descricao, itens.url_imagem 
            FROM inventario 
            JOIN itens ON inventario.item_id = itens.id 
            WHERE inventario.jogador_id = %s;
        """
        cur.execute(query, (jogador_id,))
        items_do_jogador = cur.fetchall()
        cur.close()
        conn.close()
        inventario_list = []
        for item in items_do_jogador:
            inventario_list.append({
                "inventario_id": item[0],
                "nome": item[1],
                "descricao": item[2],
                "url_imagem": item[3]
            })
        return jsonify(inventario_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # API para adicionar um item ao inventário de um jogador
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
    
    # API para listar todos os itens mestres
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
    
@app.route('/api/jogadores', methods=['GET'])
def get_jogadores():
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
# API para adicionar um novo jogador
@app.route('/api/jogador', methods=['POST'])
def adicionar_jogador():
    dados = request.get_json()
    nome_jogador = dados.get('nome')
    if not nome_jogador:
        return jsonify({'error': 'O nome do jogador é obrigatório.'}), 400
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        sql = "INSERT INTO jogadores (nome) VALUES (%s) RETURNING id;"
        cur.execute(sql, (nome_jogador,))
        novo_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'id': novo_id, 'nome': nome_jogador, 'message': 'Jogador adicionado com sucesso!'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 5
    
    # 6. INICIALIZAÇÃO DO SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)