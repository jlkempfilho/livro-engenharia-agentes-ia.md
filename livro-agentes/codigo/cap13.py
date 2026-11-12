"""Capítulo 13 - evals: mudar o prompt e ver a nota mexer."""
from evals import rodar

print("=== prompt atual ===")
atual = rodar()

# Piorando de propósito: um prompt que não manda recusar nem se ater aos trechos.
print("\n=== prompt piorado de propósito ===")
PIOR = "Você é um assistente de TI prestativo. Sempre dê uma resposta útil e completa."
pior = rodar(sistema=PIOR)

print(f"\nprompt atual: {atual[0]}/{atual[1]} | prompt piorado: {pior[0]}/{pior[1]}")
