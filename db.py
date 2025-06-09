import sqlite3

# Conectando ao banco (ou criando se não existir)
conn = sqlite3.connect('votacao.db')
cursor = conn.cursor()

# Criando a tabela ADMINISTRADOR
cursor.execute('''
CREATE TABLE IF NOT EXISTS ADMINISTRADOR (
    ID_ADM INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Nome TEXT,
    email TEXT
);
''')

# Criando a tabela ELEITOR
cursor.execute('''
CREATE TABLE IF NOT EXISTS ELEITOR (
    ID_Eleitor INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Nome TEXT,
    email TEXT UNIQUE
);
''')

# Criando a tabela VOTACAO
cursor.execute('''
CREATE TABLE IF NOT EXISTS VOTACAO (
    ID_Votacao INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Nome TEXT,
    Tema TEXT,
    Data_inicio TEXT,
    Data_final TEXT,
    Status_Votacao INTEGER
);
''')

# Criando a tabela OBJETO
cursor.execute('''
CREATE TABLE IF NOT EXISTS OBJETO (
    ID_Objeto INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    Nome TEXT,
    Foto BLOB,
    Descricao TEXT
);
''')

# Criando a tabela OBJETO_VOTACAO
cursor.execute('''
CREATE TABLE IF NOT EXISTS OBJETO_VOTACAO (
    ID_Objeto_Votacao INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    ID_Objeto INTEGER,
    ID_Votacao INTEGER,
    FOREIGN KEY (ID_Objeto) REFERENCES OBJETO(ID_Objeto),
    FOREIGN KEY (ID_Votacao) REFERENCES VOTACAO(ID_Votacao)
);
''')

# Criando a tabela ELEITOR_VOTACAO
cursor.execute('''
CREATE TABLE IF NOT EXISTS ELEITOR_VOTACAO (
    ID_Eleitor_Votacao INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    ID_Votacao INTEGER,
    ID_Eleitor INTEGER,
    Valido INTEGER,
    FOREIGN KEY (ID_Votacao) REFERENCES VOTACAO(ID_Votacao),
    FOREIGN KEY (ID_Eleitor) REFERENCES ELEITOR(ID_Eleitor)
);
''')

# Criando a tabela VOTO
cursor.execute('''
CREATE TABLE IF NOT EXISTS VOTO (
    ID_Voto INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    ID_Eleitor_Votacao INTEGER,
    ID_Objeto_Votacao INTEGER,
    FOREIGN KEY (ID_Eleitor_Votacao) REFERENCES ELEITOR_VOTACAO(ID_Eleitor_Votacao),
    FOREIGN KEY (ID_Objeto_Votacao) REFERENCES OBJETO_VOTACAO(ID_Objeto_Votacao)
);
''')

# Salvando alterações e fechando conexão
conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
