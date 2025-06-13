import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('votacao.db')
cursor = conn.cursor()

# Inserir alguns administradores
cursor.execute("INSERT INTO ADMINISTRADOR (Nome, email) VALUES (?, ?)", ("Carlos Souza", "carlos@admin.com"))
cursor.execute("INSERT INTO ADMINISTRADOR (Nome, email) VALUES (?, ?)", ("Fernanda Lima", "fernanda@admin.com"))

# Inserir algumas votações
cursor.execute("INSERT INTO VOTACAO (Nome, Tema, Data_inicio, Data_final, Status_Votacao) VALUES (?, ?, ?, ?, ?)",
               ("Eleição de Representante", "Escolha do líder de turma", "01/06/2025", "05/07/2025", 1))
cursor.execute("INSERT INTO VOTACAO (Nome, Tema, Data_inicio, Data_final, Status_Votacao) VALUES (?, ?, ?, ?, ?)",
               ("Mascote da escola", "Escolher novo mascote", "11/02/2025", "01/08/2025", 1))

# Inserir alguns eleitores
cursor.execute("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", ("Ana Silva", "ana@email.com"))
cursor.execute("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", ("João Pedro", "joao@email.com"))
cursor.execute("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", ("Mariana Costa", "mariana@email.com"))

# Associar eleitores a votações
cursor.execute("INSERT INTO ELEITOR_VOTACAO (ID_Votacao, ID_Eleitor, Valido) VALUES (?, ?, ?)", (1, 1, 1))
cursor.execute("INSERT INTO ELEITOR_VOTACAO (ID_Votacao, ID_Eleitor, Valido) VALUES (?, ?, ?)", (1, 2, 1))
cursor.execute("INSERT INTO ELEITOR_VOTACAO (ID_Votacao, ID_Eleitor, Valido) VALUES (?, ?, ?)", (2, 3, 1))

# Inserir objetos (ex: candidatos ou mascotes)
cursor.execute("INSERT INTO OBJETO (Nome, Foto, Descricao) VALUES (?, ?, ?)",
               ("Lucas Oliveira", None, "Candidato a representante."))
cursor.execute("INSERT INTO OBJETO (Nome, Foto, Descricao) VALUES (?, ?, ?)",
               ("Robô Mascote", None, "Mascote tecnológico da escola."))

# Relacionar objetos às votações
cursor.execute("INSERT INTO OBJETO_VOTACAO (ID_Objeto, ID_Votacao) VALUES (?, ?)", (1, 1))  # Lucas na eleição 1
cursor.execute("INSERT INTO OBJETO_VOTACAO (ID_Objeto, ID_Votacao) VALUES (?, ?)", (2, 2))  # Mascote na eleição 2

# Inserir votos (assumindo que ID_Eleitor_Votacao e ID_Objeto_Votacao foram 1 e 1)
cursor.execute("INSERT INTO VOTO (ID_Eleitor_Votacao, ID_Objeto_Votacao) VALUES (?, ?)", (1, 1))
cursor.execute("INSERT INTO VOTO (ID_Eleitor_Votacao, ID_Objeto_Votacao) VALUES (?, ?)", (2, 1))
cursor.execute("INSERT INTO VOTO (ID_Eleitor_Votacao, ID_Objeto_Votacao) VALUES (?, ?)", (3, 2))

# Confirmar alterações
conn.commit()
print("Dados inseridos com sucesso!")

# Fechar conexão
conn.close()
