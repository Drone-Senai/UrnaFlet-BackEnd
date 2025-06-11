from typing import Union
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
import sqlite3
import base64
from fastapi.responses import StreamingResponse
import io

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
    
@app.post("/objeto")
async def cadastrar_objeto(
    nome: str = Form(...),
    descricao: str = Form(...),
    foto: UploadFile = File(...)
):
    try:
        foto_bytes = await foto.read()
        conn = sqlite3.connect("votacao.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO OBJETO (Nome, Foto, Descricao) VALUES (?, ?, ?)",
            (nome, foto_bytes, descricao)
        )
        objeto_id = cursor.lastrowid 
        foto_base64 = base64.b64encode(foto_bytes).decode("utf-8")
        conn.commit()
        conn.close()
        return {
            "id": objeto_id,
            "nome": nome,
            "descricao": descricao
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/imagem/{id_objeto}")
def obter_imagem(id_objeto: int):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Foto FROM OBJETO WHERE ID_Objeto = ?", (id_objeto,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado[0]:
        return StreamingResponse(io.BytesIO(resultado[0]), media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")

# VOTAÇÃO


@app.get("/votacoes")
def listar_votacoes():
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ID_Votacao, Nome, Tema, Data_inicio, Data_final FROM VOTACAO")
    registros = cursor.fetchall()
    conn.close()

    colunas = ["ID_Votacao", "Nome", "Tema", "Data_inicio", "Data_final"]
    return [dict(zip(colunas, linha)) for linha in registros]

# ROTA QUE RETORNA TODAS AS VOTAÇÕES E OBJETOS

def retornar_votacoes():
    conn = sqlite3.connect('votacao.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM VOTACAO")
        registros = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]

        lista_votacoes = [dict(zip(colunas, linha)) for linha in registros]
        return lista_votacoes
    except sqlite3.Error as e:
        return {"erro": str(e)}
    finally:
        conn.close()

@app.get("/votacoes")
def read_root():
    return retornar_votacoes()

# ---------------------------------------

@app.get("/objetos")
def listar_objetos():
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    cursor.execute("SELECT ID_Objeto, Nome FROM OBJETO")
    objetos = cursor.fetchall()
    conn.close()

    return [{"id": row[0], "nome": row[1]} for row in objetos]


# ROTA QUE CRIA RELAÇÃO OBJETO_VOTACAO

class ObjetoVotacao(BaseModel):
    id_votacao: int
    id_objeto: int

@app.post("/addObjetoVotacao")
def add_objeto_votacao(obj_vot: ObjetoVotacao):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        # Verifica se já existe
        cursor.execute("""
            SELECT 1 FROM OBJETO_VOTACAO 
            WHERE ID_Votacao = ? AND ID_Objeto = ?
        """, (obj_vot.id_votacao, obj_vot.id_objeto))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Objeto já adicionado à votação.")

        cursor.execute("""
            INSERT INTO OBJETO_VOTACAO (ID_Votacao, ID_Objeto)
            VALUES (?, ?)
        """, (obj_vot.id_votacao, obj_vot.id_objeto))
        conn.commit()
        return {"message": "Objeto adicionado com sucesso"}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()