"""Capítulo 3 - embeddings: significado vira vetor."""
from embeddings import cosseno, embed

docs = ["Como emitir nota fiscal de saída no faturamento",
        "Cadastro de produtos e unidades de medida",
        "Receita de bolo de cenoura com cobertura"]
pergunta = "preciso faturar um pedido"

q = embed([pergunta], "search_query")[0]
print(f"pergunta: {pergunta}  (vetor de {len(q)} números)\n")
for doc, vetor in zip(docs, embed(docs)):
    print(f"{cosseno(q, vetor):.3f}  {doc}")

# O ponto fraco: negação.
a, b, c = embed(["pedido aprovado", "pedido não aprovado", "pedido recusado"])
print(f"\n'pedido aprovado' x 'pedido não aprovado': {cosseno(a, b):.3f}")
print(f"'pedido aprovado' x 'pedido recusado':     {cosseno(a, c):.3f}")
