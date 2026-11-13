"""Capítulo 5, parte 3 - as camadas 1 e 3 medidas: contexto no trecho e reordenação.

Camada 1: antes de indexar, o modelo escreve uma frase situando cada trecho;
          o embedding é feito de `frase + trecho`.
Camada 3: a busca híbrida traz 10 candidatos e o modelo escolhe a ordem final.
"""
import numpy as np
from pydantic import BaseModel

from banco import buscar, buscar_hibrida, carregar_manual, conectar
from cap05b import CASOS, medir
from embeddings import embed
from llm import conversar

conn = conectar()
carregar_manual(conn)
with open("dados/manual.md", encoding="utf-8") as f:
    MANUAL = f.read()
TRECHOS = [p.strip() for p in MANUAL.split("\n\n") if p.strip()]


# ---------- camada 1: contexto no trecho ----------
def situar(trecho):
    r = conversar([{"role": "user", "content":
                    f"<manual>\n{MANUAL}\n</manual>\n\n<trecho>\n{trecho}\n</trecho>\n\n"
                    "Escreva UMA frase curta que situe o trecho dentro do manual: de que assunto "
                    "ele trata e em que situação alguém o procuraria. Responda só com a frase."}],
                  max_tokens=1200, etapa="contexto")
    return r.texto.strip()


frases = [situar(t) for t in TRECHOS]
vetores = embed([f"{frase}\n{trecho}" for frase, trecho in zip(frases, TRECHOS)])


def buscar_com_contexto(conn, pergunta, k=3):
    """Mesma busca por significado, mas contra os vetores de `frase + trecho`."""
    q = embed([pergunta], "search_query")[0]
    notas = vetores @ q / (np.linalg.norm(vetores, axis=1) * np.linalg.norm(q))
    return [(TRECHOS[i], "manual", float(notas[i])) for i in np.argsort(-notas)[:k]]


# ---------- camada 3: reordenação ----------
class Ordem(BaseModel):
    melhores: list[int]   # números dos trechos, do mais útil para o menos útil


def buscar_reordenada(conn, pergunta, k=3):
    candidatos = buscar_hibrida(conn, pergunta, k=10)
    lista = "\n".join(f"[{i}] {c}" for i, (c, _, _) in enumerate(candidatos))
    r = conversar([{"role": "user", "content":
                    f"Pergunta: {pergunta}\n\nTrechos candidatos:\n{lista}\n\n"
                    f"Devolva os números dos {k} trechos que melhor respondem à pergunta, "
                    "do mais útil para o menos útil."}],
                  esquema=Ordem, max_tokens=1200, etapa="reordenar")
    validos = list(dict.fromkeys(i for i in r.dados.melhores if 0 <= i < len(candidatos)))
    return [candidatos[i] for i in validos[:k]]   # número inventado pelo modelo é descartado


print("Exemplo de frase escrita pelo modelo (trecho da VPN):")
print("  " + next(f for f, t in zip(frases, TRECHOS) if "VPN" in t) + "\n")
medir(conn, "só significado (ponto de partida)", buscar)
medir(conn, "camada 1: significado com contexto no trecho", buscar_com_contexto)
medir(conn, "camada 2: híbrida", buscar_hibrida)
medir(conn, "camadas 2 + 3: híbrida com reordenação pelo modelo", buscar_reordenada)
