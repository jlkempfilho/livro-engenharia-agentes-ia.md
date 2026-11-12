"""Capítulo 7 - o agente: tool calling em laço, com freio."""
from agente import agente
from banco import carregar_manual, conectar

conn = conectar()
carregar_manual(conn)


def mostrar(volta, nome, args, erro):
    print(f"  volta {volta}: {nome}({args}){'  [ERRO]' if erro else ''}")


for pergunta in ["O pedido 000123 está travado. Por quê, e o que eu faço para liberar?",
                 "E o pedido 000125, consigo liberar na mão?"]:
    print(f"> {pergunta}")
    resposta, voltas = agente(conn, pergunta, ao_passo=mostrar)
    print(f"  resposta ({voltas} voltas): {resposta}\n")

# O freio: com uma volta só, o agente não tem como concluir.
print("> mesma pergunta, com max_voltas=1")
print(" ", agente(conn, "O pedido 000123 está travado. O que eu faço?", max_voltas=1)[0])
