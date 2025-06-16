from typing import Union
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
import sqlite3
import base64
from fastapi.responses import StreamingResponse
import io
from uuid import uuid4
from fastapi.responses import HTMLResponse, JSONResponse

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
    # nome: str
    email: str

@app.post("/register")
def registrar(usuario: Usuario):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO ELEITOR (Nome, email) VALUES (?, ?)", ('teste', usuario.email))
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

class Votacao(BaseModel):
    nome: str
    tema: str
    data_hoje: str
    data_encerramento: str

@app.post("/addVotacao")
def registrar(votacao: Votacao):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO VOTACAO (Nome, Tema, Data_inicio, Data_final, Status_Votacao) VALUES (?, ?, ?, ?, ?)", (votacao.nome, votacao.tema, votacao.data_hoje, votacao.data_encerramento, 1))
        conn.commit()
        return {"message": "Votação adicionada com sucesso"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Votação já existente")
    finally:
        conn.close()

# --------------------------------------------------------------------

@app.get("/votacoes")
def listar_votacoes():
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ID_Votacao, Nome, Tema, Data_inicio, Data_final, Status_Votacao FROM VOTACAO")
    registros = cursor.fetchall()
    conn.close()

    colunas = ["ID_Votacao", "Nome", "Tema", "Data_inicio", "Data_final", "Status_Votacao"]
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
def listar_objetos(id_votacao: str = None):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    if not id_votacao:
        cursor.execute("SELECT ID_Objeto, Nome FROM OBJETO")
    
    else:
        cursor.execute("""
            SELECT 
                a.ID_Objeto,
                a.Nome
            FROM 
                OBJETO AS a
            JOIN OBJETO_VOTACAO AS b
                ON a.ID_Objeto = b.ID_Objeto
            WHERE b.ID_Votacao = ?
        """, (id_votacao,)) 

    objetos = cursor.fetchall()
    conn.close()

    return [{"id": row[0], "nome": row[1]} for row in objetos]

@app.get("/eleitores")
def listar_eleitores():
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    cursor.execute("SELECT ID_Eleitor, Nome FROM ELEITOR")
    eleitores = cursor.fetchall()
    conn.close()

    return [{"id": row[0], "nome": row[1]} for row in eleitores]


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
        
# ROTA QUE CRIA RELAÇÃO ELEITOR_VOTACAO

class EleitorVotacao(BaseModel):
    id_votacao: int
    id_eleitor: int
    valido: int

@app.post("/addEleitorVotacao")
def add_eleitor_votacao(elei_vot: EleitorVotacao):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        # Verifica se já existe
        cursor.execute("""
            SELECT 1 FROM ELEITOR_VOTACAO 
            WHERE ID_Votacao = ? AND ID_Eleitor = ?
        """, (elei_vot.id_votacao, elei_vot.id_eleitor))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Eleitor já adicionado à votação.")

        cursor.execute("""
            INSERT INTO ELEITOR_VOTACAO (ID_Votacao, ID_Eleitor, Valido)
            VALUES (?, ?, ?)
        """, (elei_vot.id_votacao, elei_vot.id_eleitor, elei_vot.valido))
        conn.commit()
        return {"message": "Eleitor adicionado com sucesso"}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

# ENCERRAR VOTAÇÃO

class EncerrarVotacao(BaseModel):
    id_votacao: int

@app.post("/encerrarVotacao")
def encerrar_votacao(request: EncerrarVotacao):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE VOTACAO
            SET Status_Votacao = 0
            WHERE ID_Votacao = ?
        """, (request.id_votacao,))  # vírgula para formar uma tupla!

        conn.commit()
        return {"message": f"Votação {request.id_votacao} encerrada com sucesso!"}
    
    except Exception as e:
        return {"detail": f"Erro ao encerrar votação: {e}"}
    
    finally:
        conn.close()

# CADASTRAR E ENTRAR EMAIL

@app.post("/verificar-email")
def verificar_email(data: dict):
    email = data["email"]
    
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM ELEITOR WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        return {"existe": resultado is not None}

    finally:
        conn.close()

def verificar_confirmacao(email: str):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT confirmado FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        if resultado and resultado[0]:  # resultado[0] == True
            return {"confirmado": True}
        return {"confirmado": False}
    finally:
        conn.close()

# ROTA PARA QUE VOTE 

class voto(BaseModel):
    id_votacao: int
    id_eleitor: int
    id_objeto_votacao: int

@app.post("/adicionar_voto")
def votar(request: voto):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    try:
        # Busca o ID_Eleitor_Votacao correspondente
        cursor.execute("""
            SELECT ID_Eleitor_Votacao FROM ELEITOR_VOTACAO
            WHERE ID_Eleitor = ? AND ID_Votacao = ?
        """, (request.id_eleitor, request.id_votacao))
        
        resultado = cursor.fetchone()
        if not resultado:
            return {"erro": "Eleitor não está registrado para essa votação."}

        id_eleitor_votacao = resultado[0]

        # Verifica se já existe voto
        cursor.execute("""
            SELECT 1 FROM VOTO
            WHERE ID_Eleitor_Votacao = ?
        """, (id_eleitor_votacao,))
        
        if cursor.fetchone():
            return {"ja_votou": True, "mensagem": "Eleitor já votou nesta votação."}

        # Caso não tenha votado, insere o voto
        cursor.execute("""
            INSERT INTO VOTO (ID_Eleitor_Votacao, ID_Objeto_Votacao)
            VALUES (?, ?)
        """, (id_eleitor_votacao, request.id_objeto_votacao))

        conn.commit()
        return {"voto_registrado": True, "mensagem": "Voto registrado com sucesso."}
    
    except sqlite3.Error as e:
        return {"erro": str(e)}

    finally:
        conn.close()


@app.get("/confirmar")
def confirmar_email(email: str):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE CONFIRMACAO_EMAIL SET confirmado = 1 WHERE email = ?", (email,))
        conn.commit()
        return HTMLResponse("<h2 style='color:green;'>Email confirmado com sucesso! Você pode voltar à plataforma.</h2>")
    except Exception as e:
        return HTMLResponse(f"<h2>Erro: {e}</h2>", status_code=500)
    finally:
        conn.close()

@app.get("/confirmado")
def confirmado(email: str):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT confirmado FROM CONFIRMACAO_EMAIL WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and row[0] == 1:
            return {"confirmado": True}
        return {"confirmado": False}
    finally:
        conn.close()

@app.post("/registrar-token")
def registrar_token(data: dict):
    email = data["email"]
    token = str(uuid4())
    
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO CONFIRMACAO_EMAIL (email, token, confirmado)
            VALUES (?, ?, 0)
            ON CONFLICT(email) DO UPDATE SET token = excluded.token, confirmado = 0
        """, (email, token))
        conn.commit()
        return {"token": token}
    finally:
        conn.close()
        
# ROTA DO RESULTADO DA VOTAÇÃO

@app.get("/resultados")
def retornar_resultados(id_votacao: str = None):
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            O.ID_Objeto,
            O.Nome,
            COUNT(V.ID_Voto) AS Total_Votos
        FROM 
            VOTO V
        JOIN OBJETO_VOTACAO OV 
            ON V.ID_Objeto_Votacao = OV.ID_Objeto_Votacao
        JOIN OBJETO O 
            ON OV.ID_Objeto = O.ID_Objeto
        WHERE OV.ID_Votacao = ?
        GROUP BY O.ID_Objeto, O.Nome
        ORDER BY Total_Votos DESC
    """, (id_votacao,))

    resultados = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "nome": row[1], "total_votos": row[2]}
        for row in resultados
    ]

@app.post("/verificar-administrador")
def verificar_administrador(dados: dict):
    email = dados.get("email")
    conn = sqlite3.connect("votacao.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ADMINISTRADOR WHERE Email = ?", (email,))
    admin = cursor.fetchone()
    conn.close()
    return {"administrador": bool(admin)}
