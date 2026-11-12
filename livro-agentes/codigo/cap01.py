"""Capítulo 1 - a primeira chamada a um modelo de linguagem."""
from llm import MODELO, PROVEDOR, conversar

print(f"provedor: {PROVEDOR} | modelo: {MODELO}\n")

r = conversar([{"role": "user", "content": "Em uma frase: o que é um ERP?"}], etapa="cap01")
print(r.texto)
print(f"[tokens de entrada: {r.entrada} | de saída: {r.saida} | {r.ms} ms]\n")

# O mesmo número de palavras não custa o mesmo número de tokens.
for frase in ["o gato subiu no telhado da casa", "Protheus SIGAFAT MATA410 SF2010 SEFAZ"]:
    r = conversar([{"role": "user", "content": frase}], max_tokens=16, etapa="cap01")
    print(f"{len(frase.split())} palavras -> {r.entrada} tokens de entrada: {frase}")

# Uma pergunta que o modelo não tem como saber.
r = conversar([{"role": "user",
                "content": "Qual é o status do pedido de venda 000123 da minha empresa?"}],
              etapa="cap01")
print("\nPergunta impossível:", r.texto[:300])
