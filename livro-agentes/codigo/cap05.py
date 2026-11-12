"""Capítulo 5 - RAG: buscar e só então responder."""
from banco import carregar_manual, conectar
from rag import responder

conn = conectar()
carregar_manual(conn)

for pergunta in ["Como libero um pedido travado por crédito?",
                 "Até quando posso cancelar uma nota fiscal?",
                 "Qual a alíquota de ICMS em São Paulo?"]:   # não está no manual
    r = responder(conn, pergunta)
    print(f"> {pergunta}\n{r.texto}\n  [entrada: {r.entrada} tokens]\n")
