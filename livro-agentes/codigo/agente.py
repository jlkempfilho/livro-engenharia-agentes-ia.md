"""agente.py - o laço: o modelo decide os passos, o código executa (capítulo 7)."""
from ferramentas import FERRAMENTAS, executar
from llm import conversar_com_reserva

SISTEMA = """Você é o assistente de suporte de TI de uma empresa.
Regras:
1. Se o usuário citar um número de pedido, chame consultar_pedido.
2. Antes de dizer COMO resolver qualquer problema ou bloqueio, chame buscar_manual
   com o problema encontrado. O procedimento correto está sempre no manual.
3. Responda em português, de forma curta, só com o que as ferramentas trouxeram.
4. Se as ferramentas não trouxerem a resposta, diga que não encontrou. Não invente."""


def agente(conn, pergunta, max_voltas=6, ao_texto=None, ao_passo=None):
    """Devolve (resposta_final, voltas_usadas)."""
    mensagens = [{"role": "user", "content": pergunta}]
    for volta in range(1, max_voltas + 1):
        r = conversar_com_reserva(mensagens, sistema=SISTEMA, ferramentas=FERRAMENTAS,
                                  ao_texto=ao_texto, etapa="agente")
        mensagens.append(r.mensagem())
        if r.parada != "ferramenta":
            return r.texto, volta
        for c in r.chamadas:
            saida, erro = executar(conn, c.nome, c.args)
            if ao_passo:
                ao_passo(volta, c.nome, c.args, erro)
            mensagens.append({"role": "tool", "id": c.id, "content": saida, "erro": erro})
    return "Parei: limite de voltas atingido sem concluir.", max_voltas
