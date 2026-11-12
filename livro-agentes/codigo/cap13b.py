"""Capítulo 13, parte 2 - o juiz também precisa ser avaliado.

Doze respostas rotuladas por um humano (8 certas, 4 erradas). O juiz concorda com o humano?
"""
from evals import juiz

G1 = "Pela rotina Financeiro > Liberação de Crédito, por um analista de crédito."
G2 = "Em até 24 horas da emissão, em Faturamento > Cancelamento de Documento."
G3 = "Todo dia às 2h; restauração só com autorização da gerência de TI."
P1, P2, P3 = ("Como libero um pedido bloqueado por crédito?",
              "Até quando posso cancelar uma nota fiscal?", "Que horas roda o backup do ERP?")

# (pergunta, resposta avaliada, gabarito, rótulo humano: a resposta está certa?)
ROTULADAS = [
    (P1, "Vá em Financeiro > Liberação de Crédito; quem libera é o analista de crédito.", G1, True),
    (P1, "A liberação é feita por um analista de crédito na rotina de Liberação de Crédito do Financeiro.", G1, True),
    (P1, "Peça a um analista de crédito para liberar em Financeiro > Liberação de Crédito.", G1, True),
    (P2, "Você tem 24 horas depois de emitir. Use Faturamento > Cancelamento de Documento.", G2, True),
    (P2, "O prazo é de um dia a partir da emissão, na rotina Cancelamento de Documento do Faturamento.", G2, True),
    (P3, "O backup roda diariamente às 2 da manhã. Para restaurar, precisa de autorização da gerência de TI.", G3, True),
    (P3, "Às 2h, todos os dias.", G3, True),
    (P2, "Dentro de 24h da emissão.", G2, True),
    (P1, "Qualquer usuário libera o pedido em Faturamento > Liberação de Pedidos.", G1, False),
    (P2, "Você pode cancelar em até 48 horas, em Faturamento > Cancelamento de Documento.", G2, False),
    (P3, "O backup roda toda semana, aos domingos, às 2h.", G3, False),
    (P1, "Pedido bloqueado por crédito é liberado sozinho quando o cliente paga; não há rotina.", G1, False),
]


def medir(nome, julgar):
    vp = vn = fp = fn = 0
    for pergunta, resposta, gabarito, certa in ROTULADAS:
        aprovou = julgar(pergunta, resposta, gabarito)
        vp += certa and aprovou
        fn += certa and not aprovou
        vn += (not certa) and (not aprovou)
        fp += (not certa) and aprovou
    total = len(ROTULADAS)
    print(f"=== {nome} ===")
    print(f"  concordância com o humano: {vp + vn}/{total} ({100 * (vp + vn) // total}%)")
    print(f"  aprova o que está certo:  {vp}/{vp + fn}   (taxa de verdadeiros positivos)")
    print(f"  barra o que está errado:  {vn}/{vn + fp}   (taxa de verdadeiros negativos)\n")


medir("juiz preguiçoso (aprova tudo, sem olhar)", lambda p, r, g: True)
medir("juiz LLM", lambda p, r, g: juiz(p, r, g).correto)
