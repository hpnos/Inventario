# Arquivo: database.py
import psycopg2
import os

# --- CONEXÃO COM O POSTGRESQL ---
# É uma boa prática pegar a URL de uma variável de ambiente, 
# mas para simplificar, vamos colá-la aqui por enquanto.
# SUBSTITUA PELA SUA URL INTERNA DO BANCO DE DADOS DA RENDER
DATABASE_URL = "postgresql://inventario_17xg_user:4hWbh4QtH9XX2UoS10WdlzkGLZnCcmpN@dpg-d3noj22dbo4c73d5sg6g-a.oregon-postgres.render.com/inventario_17xg"

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- FUNÇÕES DO BANCO (ADAPTADAS PARA POSTGRES) ---

def inicializar():
    """Cria as tabelas no PostgreSQL se elas não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sintaxe ligeiramente diferente para autoincremento (SERIAL) e chaves estrangeiras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id SERIAL PRIMARY KEY,
            jogador_id INTEGER NOT NULL,
            nome_item TEXT NOT NULL,
            descricao TEXT,
            quantidade INTEGER NOT NULL DEFAULT 1,
            CONSTRAINT fk_jogador
                FOREIGN KEY(jogador_id) 
                REFERENCES jogadores(id)
                ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabelas verificadas/criadas no PostgreSQL com sucesso!")

def adicionar_jogador(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Placeholders no psycopg2 são '%s' em vez de '?'
        cursor.execute("INSERT INTO jogadores (nome) VALUES (%s)", (nome,))
        conn.commit()
    except psycopg2.IntegrityError:
        print(f"O jogador '{nome}' já existe no banco de dados.")
        conn.rollback() # Desfaz a transação em caso de erro
    finally:
        cursor.close()
        conn.close()

def listar_jogadores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM jogadores ORDER BY nome")
    jogadores = cursor.fetchall()
    cursor.close()
    conn.close()
    return jogadores

def adicionar_item(jogador_id, nome_item, descricao, quantidade):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventario (jogador_id, nome_item, descricao, quantidade) VALUES (%s, %s, %s, %s)",
        (jogador_id, nome_item, descricao, quantidade)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_itens_por_jogador(jogador_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_item, descricao, quantidade FROM inventario WHERE jogador_id = %s", (jogador_id,))
    itens = cursor.fetchall()
    cursor.close()
    conn.close()
    return itens

def obter_jogador_por_id(jogador_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM jogadores WHERE id = %s", (jogador_id,))
    jogador = cursor.fetchone()
    cursor.close()
    conn.close()
    if jogador:
        return jogador[0]
    return None

def listar_inventarios_completos():
    conn = get_db_connection()
    cursor = conn.cursor()
    inventarios = {}
    cursor.execute("SELECT id, nome FROM jogadores ORDER BY nome")
    jogadores = cursor.fetchall()
    for jogador_id, nome_jogador in jogadores:
        cursor.execute(
            "SELECT nome_item, descricao, quantidade FROM inventario WHERE jogador_id = %s ORDER BY nome_item",
            (jogador_id,)
        )
        itens = cursor.fetchall()
        inventarios[nome_jogador] = itens
    cursor.close()
    conn.close()
    return inventarios

# Se você rodar 'python database.py' localmente, ele criará as tabelas no banco da Render.
if __name__ == '__main__':
    inicializar()