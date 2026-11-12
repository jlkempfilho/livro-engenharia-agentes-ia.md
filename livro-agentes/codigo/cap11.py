"""Capítulo 11 - cache de prompt: prefixo estável primeiro, o que muda por último."""
import time

from llm import PROVEDOR, conversar

with open("dados/manual.md", encoding="utf-8") as f:
    MANUAL = f.read() * 6          # prefixo longo, para o efeito aparecer

SISTEMA_ESTAVEL = f"Você responde em uma frase sobre o manual abaixo.\n\n{MANUAL}"


def medir(titulo, sistema_de):
    print(f"=== {titulo} ===")
    for pergunta in ["Onde emito nota de saída?", "Quando roda o backup?",
                     "Como peço acesso à VPN?"]:
        r = conversar([{"role": "user", "content": pergunta}],
                      sistema=sistema_de(), max_tokens=100, etapa="cap11")
        print(f"  {r.ms:>6} ms | entrada {r.entrada} | lidos do cache {r.cache_lido} | {pergunta}")
    print()


print(f"provedor: {PROVEDOR}\n")
medir("prefixo ESTÁVEL (o cache funciona)", lambda: SISTEMA_ESTAVEL)
medir("prefixo com HORA no começo (o cache morre)",
      lambda: f"Agora são {time.time()}.\n{SISTEMA_ESTAVEL}")
