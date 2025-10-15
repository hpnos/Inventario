# Arquivo: database.py (versão atualizada)
import psycopg2
DATABASE_URL = "postgresql://inventario_17xg_user:4hWbh4QtH9XX2UoS10WdlzkGLZnCcmpN@dpg-d3noj22dbo4c73d5sg6g-a/inventario_17xg" # Lembre de usar a URL INTERNA

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# ... (as funções de jogador continuam as mesmas: inicializar, adicionar_jogador, listar_jogadores, obter_jogador_por_id) ...

# --- NOVAS FUNÇÕES PARA ITENS MESTRE ---
def adicionar_item_mestre(nome, descricao, imagem_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO itens_mestre (nome, descricao, imagem_url) VALUES (%s, %s, %s)",
        (nome, descricao, imagem_url)
    )
    conn.commit()
    cursor.close()
    conn.close()

def listar_itens_mestre():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, descricao, imagem_url FROM itens_mestre ORDER BY nome")
    itens = cursor.fetchall()
    cursor.close()
    conn.close()
    return itens

# --- FUNÇÕES DE INVENTÁRIO ATUALIZADAS ---
def adicionar_item_ao_inventario(jogador_id, item_mestre_id, quantidade):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Lógica para verificar se o item já existe e somar a quantidade pode ser adicionada aqui
    cursor.execute(
        "INSERT INTO inventario (jogador_id, item_mestre_id, quantidade) VALUES (%s, %s, %s)",
        (jogador_id, item_mestre_id, quantidade)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Em database.py, substitua a função listar_inventarios_completos

def listar_inventarios_completos():
    """
    Busca todos os jogadores e agrupa seus itens para a página de visualização,
    usando a nova estrutura com JOIN.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    inventarios = {}
    
    # 1. Pega todos os jogadores
    cursor.execute("SELECT id, nome FROM jogadores ORDER BY nome")
    jogadores = cursor.fetchall()

    # 2. Para cada jogador, busca seus itens usando JOIN
    for jogador_id, nome_jogador in jogadores:
        cursor.execute("""
            SELECT im.nome, im.descricao, inv.quantidade, im.imagem_url
            FROM inventario inv
            JOIN itens_mestre im ON inv.item_mestre_id = im.id
            WHERE inv.jogador_id = %s
            ORDER BY im.nome
        """, (jogador_id,))
        itens = cursor.fetchall()
        inventarios[nome_jogador] = itens
        
    cursor.close()
    conn.close()
    return inventarios

def listar_inventarios_completos():
    # ... (esta função precisaria ser reescrita com JOINs também, podemos fazer depois se necessário) ...
    # Por enquanto, vamos focar na página de admin.
    pass