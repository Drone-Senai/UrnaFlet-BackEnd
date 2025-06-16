import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('votacao.db')
cursor = conn.cursor()

# Inserir administradores
admins = [
    ("Carlos Souza", "carlos@admin.com"),
    ("Fernanda Lima", "fernanda@admin.com"),
    ("João Alves", "joaoalves@admin.com"),
    ("Patrícia Gomes", "patricia@admin.com")
]
cursor.executemany("INSERT INTO ADMINISTRADOR (Nome, email) VALUES (?, ?)", admins)

# Inserir votações (com datas no formato dd/mm/aaaa)
votacoes = [
    ("Eleição de Representante", "Escolha do líder de turma", "01/06/2025", "05/07/2025", 1),
    ("Mascote da escola", "Escolher novo mascote", "11/02/2025", "01/08/2025", 1),
    ("Nova cor do uniforme", "Escolher cor do uniforme", "01/03/2025", "15/03/2025", 1),
    ("Tema da festa junina", "Votação do tema", "20/05/2025", "20/06/2025", 0),
    ("Atividade extra", "Escolher entre esporte ou arte", "10/04/2025", "30/04/2025", 1)
]
cursor.executemany("""
    INSERT INTO VOTACAO (Nome, Tema, Data_inicio, Data_final, Status_Votacao)
    VALUES (?, ?, ?, ?, ?)
""", votacoes)

# Inserir eleitores
eleitores = [
    ("Ana Silva", "ana@email.com"),
    ("João Pedro", "joao@email.com"),
    ("Mariana Costa", "mariana@email.com"),
    ("Carlos Oliveira", "carlos.oli@email.com"),
    ("Lívia Martins", "livia@email.com"),
    ("Rafael Souza", "rafael@email.com"),
    ("Beatriz Ramos", "beatriz@email.com"),
    ("Paulo Mendes", "paulo@email.com"),
    ("Juliana Rocha", "juliana@email.com"),
    ("Gabriel Lima", "gabriel@email.com")
]
cursor.executemany("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", eleitores)

# Associar eleitores às votações
eleitor_votacao = []
for id_votacao in range(1, 6):  # 5 votações
    for id_eleitor in range(1, 11):  # 10 eleitores
        eleitor_votacao.append((id_votacao, id_eleitor, 1))
cursor.executemany("INSERT INTO ELEITOR_VOTACAO (ID_Votacao, ID_Eleitor, Valido) VALUES (?, ?, ?)", eleitor_votacao)

# Inserir objetos
objetos = [
    ("Lucas Oliveira", None, "Candidato a representante."),
    ("Robô Mascote", None, "Mascote tecnológico da escola."),
    ("Uniforme Azul", None, "Uniforme com tons de azul."),
    ("Festa Caipira", None, "Tema tradicional junino."),
    ("Esportes", None, "Atividades de futebol, vôlei, basquete."),
    ("Maria Souza", None, "Candidata a representante."),
    ("Mascote Dragão", None, "Dragão com as cores da escola."),
    ("Uniforme Laranja", None, "Moderno e vibrante."),
    ("Festa Medieval", None, "Inspirada na idade média."),
    ("Artes", None, "Pintura, teatro e música.")
]
cursor.executemany("INSERT INTO OBJETO (Nome, Foto, Descricao) VALUES (?, ?, ?)", objetos)

# Relacionar objetos às votações
objeto_votacao = [
    (1, 1), (6, 1),  # Representante
    (2, 2), (7, 2),  # Mascote
    (3, 3), (8, 3),  # Uniforme
    (4, 4), (9, 4),  # Festa
    (5, 5), (10, 5)  # Atividade
]
cursor.executemany("INSERT INTO OBJETO_VOTACAO (ID_Objeto, ID_Votacao) VALUES (?, ?)", objeto_votacao)

# Inserir votos
cursor.execute("SELECT ID_Eleitor_Votacao FROM ELEITOR_VOTACAO")
eleitor_votacao_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT ID_Objeto_Votacao, ID_Votacao FROM OBJETO_VOTACAO")
objeto_votacao_dict = {}
for id_objeto_votacao, id_votacao in cursor.fetchall():
    objeto_votacao_dict.setdefault(id_votacao, []).append(id_objeto_votacao)

votos = []
for id_votacao in range(1, 6):
    objetos_votacao = objeto_votacao_dict[id_votacao]
    votos_feitos = 0
    for id_ev in eleitor_votacao_ids:
        cursor.execute("SELECT ID_Votacao FROM ELEITOR_VOTACAO WHERE ID_Eleitor_Votacao = ?", (id_ev,))
        if cursor.fetchone()[0] == id_votacao:
            votos.append((id_ev, objetos_votacao[votos_feitos % len(objetos_votacao)]))
            votos_feitos += 1
            if votos_feitos >= 5:
                break

cursor.executemany("INSERT INTO VOTO (ID_Eleitor_Votacao, ID_Objeto_Votacao) VALUES (?, ?)", votos)

# Confirmar e fechar
conn.commit()
print("Dados inseridos com sucesso!")
conn.close()
