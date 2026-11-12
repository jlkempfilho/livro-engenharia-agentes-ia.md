"""observa.py - registro de cada chamada ao modelo (capítulo 14)."""
import json
import os
from datetime import datetime

ARQUIVO = os.getenv("LOG_CHAMADAS", "chamadas.jsonl")


def registrar(registro):
    registro = {"quando": datetime.now().isoformat(timespec="seconds"), **registro}
    with open(ARQUIVO, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def ler():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def resumo(desde=0):
    """Resumo das chamadas a partir da posição `desde` do log."""
    linhas = ler()[desde:]
    ok = [l for l in linhas if "erro" not in l]
    por_etapa = {}
    for l in ok:
        e = por_etapa.setdefault(l["etapa"], {"chamadas": 0, "entrada": 0, "saida": 0, "ms": 0})
        e["chamadas"] += 1
        e["entrada"] += l["entrada"]
        e["saida"] += l["saida"]
        e["ms"] += l["ms"]
    return {
        "chamadas": len(linhas),
        "erros": len(linhas) - len(ok),
        "tokens_entrada": sum(l["entrada"] for l in ok),
        "tokens_saida": sum(l["saida"] for l in ok),
        "cache_lido": sum(l["cache_lido"] for l in ok),
        "mais_lenta_ms": max((l["ms"] for l in ok), default=0),
        "cortadas_por_limite": sum(l["parada"] == "limite" for l in ok),
        "por_etapa": por_etapa,
    }
