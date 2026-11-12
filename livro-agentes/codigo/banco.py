"""banco.py - banco vetorial em PostgreSQL + pgvector (capítulo 4)."""
import os
import re

import psycopg
from pgvector.psycopg import register_vector

from embeddings import DIMENSOES, embed

DSN = os.getenv("DSN", "postgresql://postgres:livro@banco:5432/postgres")


def conectar():
    conn = psycopg.connect(DSN, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    conn.execute(f"""CREATE TABLE IF NOT EXISTS trechos (
        id serial PRIMARY KEY, fonte text NOT NULL, conteudo text NOT NULL,
        embedding vector({DIMENSOES}), UNIQUE (fonte, conteudo))""")
    conn.execute("""CREATE INDEX IF NOT EXISTS trechos_hnsw
        ON trechos USING hnsw (embedding vector_cosine_ops)""")
    return conn


def inserir(conn, fonte, textos):
    for texto, vetor in zip(textos, embed(textos)):
        conn.execute("""INSERT INTO trechos (fonte, conteudo, embedding) VALUES (%s, %s, %s)
                        ON CONFLICT (fonte, conteudo) DO NOTHING""", (fonte, texto, vetor))


def carregar_manual(conn, caminho="dados/manual.md"):
    with open(caminho, encoding="utf-8") as f:
        trechos = [p.strip() for p in f.read().split("\n\n") if p.strip()]
    inserir(conn, "manual", trechos)
    return len(trechos)


def buscar(conn, pergunta, k=3, fontes=None):
    """Os k trechos mais parecidos com a pergunta. `fontes` restringe a origem (cap. 10)."""
    q = embed([pergunta], "search_query")[0]
    filtro, params = "", [q]
    if fontes:
        filtro = "WHERE fonte = ANY(%s)"
        params.append(list(fontes))
    params += [q, k]
    return conn.execute(f"""SELECT conteudo, fonte, 1 - (embedding <=> %s) AS semelhanca
        FROM trechos {filtro} ORDER BY embedding <=> %s LIMIT %s""", params).fetchall()


def buscar_palavras(conn, pergunta, k=3, fontes=None):
    """Busca por palavra-chave (texto completo do PostgreSQL). Acha código e termo exato."""
    palavras = [p for p in re.findall(r"\w+", pergunta.lower()) if len(p) >= 3]
    if not palavras:
        return []
    filtro, params = "", [" | ".join(palavras)]
    if fontes:
        filtro = "AND fonte = ANY(%s)"
        params.append(list(fontes))
    params.append(k)
    return conn.execute(f"""
        SELECT conteudo, fonte, ts_rank(to_tsvector('portuguese', conteudo), q) AS nota
        FROM trechos, to_tsquery('portuguese', %s) AS q
        WHERE to_tsvector('portuguese', conteudo) @@ q {filtro}
        ORDER BY nota DESC LIMIT %s""", params).fetchall()


def buscar_hibrida(conn, pergunta, k=3, fontes=None, candidatos=10):
    """Junta a busca por significado com a busca por palavra (Reciprocal Rank Fusion).

    Cada lista vota: um trecho na posição p recebe 1 / (60 + p). Somam-se os votos.
    Quem aparece bem nas duas listas sobe; quem só aparece numa ainda pode entrar.
    """
    pontos, dados = {}, {}
    for lista in (buscar(conn, pergunta, candidatos, fontes),
                  buscar_palavras(conn, pergunta, candidatos, fontes)):
        for posicao, (conteudo, fonte, _) in enumerate(lista, start=1):
            pontos[conteudo] = pontos.get(conteudo, 0) + 1 / (60 + posicao)
            dados[conteudo] = fonte
    ordenados = sorted(pontos, key=pontos.get, reverse=True)[:k]
    return [(c, dados[c], pontos[c]) for c in ordenados]
