"""embeddings.py - texto vira vetor (capítulo 3).

O fornecedor de embeddings é independente do fornecedor do chat:
aqui é sempre um endpoint no dialeto OpenAI (por padrão, o Ollama local).
"""
import os

import numpy as np
from openai import OpenAI

MODELO = os.getenv("EMBED_MODELO", "nomic-embed-text")
DIMENSOES = 768
_cliente = OpenAI(base_url=os.getenv("EMBED_URL", "http://ollama:11434/v1"),
                  api_key=os.getenv("EMBED_CHAVE", "ollama"))


def embed(textos, tipo="search_document"):
    """tipo: 'search_document' para o que é guardado, 'search_query' para a pergunta."""
    r = _cliente.embeddings.create(model=MODELO, input=[f"{tipo}: {t}" for t in textos])
    return np.array([d.embedding for d in r.data])


def cosseno(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
