"""triagem.py - classificar o chamado em formato garantido (capítulo 8)."""
from typing import Literal

from pydantic import BaseModel

from llm import conversar


class Chamado(BaseModel):
    categoria: Literal["acesso", "erp", "hardware", "rede", "outro"]
    prioridade: Literal["baixa", "media", "alta"]
    resumo: str
    precisa_humano: bool


SISTEMA = """Classifique o chamado de TI.
prioridade alta: operação parada ou muitas pessoas afetadas.
precisa_humano: true quando exige ação física, autorização ou decisão de gestão.
resumo: uma única frase, com no máximo 25 palavras."""


def triar(texto):
    r = conversar([{"role": "user", "content": texto}], sistema=SISTEMA,
                  esquema=Chamado, max_tokens=1200, etapa="triagem")
    return r.dados
