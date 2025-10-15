# Arquivo: app.py
# Adicione 'session' e 'flash' às importações
from flask import Flask, render_template, request, redirect, url_for, session, flash
import database as db

app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# A sessão precisa de uma chave secreta para ser segura.
# Em uma aplicação real, essa chave deve ser mais complexa e mantida em segredo.
app.secret_key = 'sua_chave_secreta_pode_ser_qualquer_coisa'

# Defina sua senha de administrador aqui.
ADMIN_PASSWORD = '5689' # Mude para uma senha de sua preferência

# --- ROTA PÚBLICA (NÃO MUDA) ---
@app.route('/')
def index():
    inventarios_completos = db.listar_inventarios_completos()
    return render_template('index.html', inventarios=inventarios_completos)

# --- NOVAS ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Verifica se a senha enviada no formulário é a correta
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True # Armazena na sessão que o usuário logou
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Senha inválida. Tente novamente.', 'danger')
            return redirect(url_for('login'))
    
    # Se o método for GET, apenas mostra a página de login
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None) # Remove a informação de login da sessão
    flash('Você saiu da área administrativa.', 'info')
    return redirect(url_for('login'))


# --- ROTAS PROTEGIDAS ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # VERIFICAÇÃO: Se o usuário não estiver logado, redireciona para o login
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_jogador = request.form['nome_jogador']
        if nome_jogador:
            db.adicionar_jogador(nome_jogador)
        return redirect(url_for('admin'))

    lista_de_jogadores = db.listar_jogadores()
    return render_template('admin.html', jogadores=lista_de_jogadores)


@app.route('/jogador/<int:jogador_id>', methods=['GET', 'POST'])
def gerenciar_jogador(jogador_id):
    # VERIFICAÇÃO: Se o usuário não estiver logado, redireciona para o login
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_item = request.form['nome_item']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']
        
        if nome_item and quantidade:
            db.adicionar_item(jogador_id, nome_item, descricao, int(quantidade))
        return redirect(url_for('gerenciar_jogador', jogador_id=jogador_id))

    nome_do_jogador = db.obter_jogador_por_id(jogador_id)
    inventario_do_jogador = db.listar_itens_por_jogador(jogador_id)

    if nome_do_jogador is None:
        return redirect(url_for('admin'))
    
    return render_template('jogador.html', 
                           nome=nome_do_jogador, 
                           inventario=inventario_do_jogador,
                           jogador_id=jogador_id)

if __name__ == '__main__':
    app.run(debug=True)