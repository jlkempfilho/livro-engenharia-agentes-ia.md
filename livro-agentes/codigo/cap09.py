"""Capítulo 9 - streaming: a mesma resposta, percebida de outro jeito."""
import time

from llm import conversar

PERGUNTA = [{"role": "user", "content": "Explique em 4 parágrafos curtos o que é um ERP."}]

# Sem streaming: silêncio até o fim.
inicio = time.time()
r = conversar(PERGUNTA, etapa="cap09")
print(f"SEM streaming: {time.time() - inicio:.2f}s olhando para a tela parada "
      f"({r.saida} tokens)\n")

# Com streaming: cada pedaço aparece assim que é gerado.
inicio, primeiro = time.time(), []


def mostrar(pedaco):
    if not primeiro:
        primeiro.append(time.time() - inicio)
    print(pedaco, end="", flush=True)


r = conversar(PERGUNTA, ao_texto=mostrar, etapa="cap09")
print(f"\n\nCOM streaming: primeira palavra em {primeiro[0]:.2f}s | "
      f"total {time.time() - inicio:.2f}s ({r.saida} tokens)")
