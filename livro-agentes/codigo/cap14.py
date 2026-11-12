"""Capítulo 14 - observabilidade: o que o log já sabe sobre o seu sistema."""
import json

import observa
from agente import agente
from banco import carregar_manual, conectar
from triagem import triar

conn = conectar()
carregar_manual(conn)
inicio = len(observa.ler())          # só o que acontecer daqui para a frente

triar("O pedido 000123 não fatura e o cliente está esperando no balcão.")
agente(conn, "O pedido 000123 está travado. O que eu faço?")
agente(conn, "Como peço acesso à VPN?")

print("últimas linhas do log:")
for linha in observa.ler()[-3:]:
    print(" ", json.dumps(linha, ensure_ascii=False))

r = observa.resumo(desde=inicio)
print(f"\nchamadas: {r['chamadas']} | erros: {r['erros']}")
print(f"tokens: {r['tokens_entrada']} de entrada, {r['tokens_saida']} de saída, "
      f"{r['cache_lido']} lidos do cache")
print(f"chamada mais lenta: {r['mais_lenta_ms']} ms | cortadas por limite: "
      f"{r['cortadas_por_limite']}")
print("\npor etapa:")
for etapa, e in r["por_etapa"].items():
    print(f"  {etapa:<8} {e['chamadas']} chamadas | {e['entrada']} tokens de entrada | "
          f"{e['ms'] // e['chamadas']} ms em média")

# Custo: tokens x preço da tabela do SEU fornecedor (por milhão de tokens).
PRECO_ENTRADA, PRECO_SAIDA = 0.0, 0.0      # modelo local = 0; preencha com a tabela vigente
custo = (r["tokens_entrada"] * PRECO_ENTRADA + r["tokens_saida"] * PRECO_SAIDA) / 1_000_000
print(f"\ncusto estimado desta execução: US$ {custo:.4f}")
