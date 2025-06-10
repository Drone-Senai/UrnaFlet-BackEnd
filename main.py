from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3

app = FastAPI()

def carregar_dados_como_objetos():
    conn = sqlite3.connect('votacao.db')
    cursor = conn.cursor()

    dados_banco = {}

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    for tabela in tabelas:
        nome_tabela = tabela[0]
        try:
            cursor.execute(f"SELECT * FROM {nome_tabela}")
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]

            lista_objetos = [
                dict(zip(colunas, linha)) for linha in registros
            ]

            dados_banco[nome_tabela] = lista_objetos

        except sqlite3.Error as e:
            dados_banco[nome_tabela] = {"erro": str(e)}

    conn.close()
    return dados_banco

@app.get("/")
def read_root():
    return carregar_dados_como_objetos()


# @app.get("/teste")
# def read_root():
#     return 
class Usuario(BaseModel):
    nome: str
    email: str

@app.post("/register")
def registrar(usuario: Usuario):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", (usuario.nome, usuario.email))
        conn.commit()
        return {"message": "Usuário registrado com sucesso"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    finally:
        conn.close()

@app.post("/login")
def login(usuario: Usuario):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ELEITOR WHERE Nome=? AND email=?", (usuario.nome, usuario.email))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return {"access_token": "fake-jwt-token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")