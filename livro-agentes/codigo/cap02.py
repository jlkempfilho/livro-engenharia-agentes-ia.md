"""Capítulo 2 - a conversa é o histórico reenviado a cada chamada."""
from llm import conversar

SISTEMA = "Você é um tutor de TI. Responda em no máximo 2 frases."
PERGUNTAS = ["O que é um índice num banco de dados?",
             "E qual a desvantagem dele?",
             "Resuma em uma frase o que conversamos."]


def conversa(guardar_respostas):
    historico = []
    for pergunta in PERGUNTAS:
        historico.append({"role": "user", "content": pergunta})
        r = conversar(historico, sistema=SISTEMA, etapa="cap02")
        if guardar_respostas:
            historico.append(r.mensagem())
        print(f"> {pergunta}\n{r.texto}\n  [entrada: {r.entrada} tokens]\n")


print("=== COM memória (histórico completo) ===")
conversa(guardar_respostas=True)
print("=== SEM guardar as respostas do assistente ===")
conversa(guardar_respostas=False)
