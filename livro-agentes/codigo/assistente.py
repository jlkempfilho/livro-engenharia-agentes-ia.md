"""assistente.py - o assistente de chamados completo (capítulo 15).

Uso:
  python assistente.py "descrição do problema"
  python assistente.py            (modo conversa; linha vazia encerra)
"""
import sys

import observa
from agente import agente
from banco import carregar_manual, conectar
from llm import ErroDefinitivo, ErroTemporario
from triagem import triar


def atender(conn, texto):
    inicio = len(observa.ler())
    try:
        chamado = triar(texto)                                         # cap. 8
        print(f"[triagem] {chamado.categoria} | prioridade {chamado.prioridade} | "
              f"{'encaminhar a um humano' if chamado.precisa_humano else 'autoatendimento'}")
        print(f"[resumo]  {chamado.resumo}\n")
        agente(conn, texto,                                            # cap. 5, 6, 7, 10, 12
               ao_texto=lambda p: print(p, end="", flush=True),        # cap. 9
               ao_passo=lambda v, n, a, e: print(f"[passo {v}] {n}({a})"))
        print()
    except ErroTemporario:
        print("Assistente indisponível no momento. Abra um chamado pelo portal.")
    except ErroDefinitivo:
        print("Erro interno do assistente. A equipe de TI foi avisada.")
    r = observa.resumo(desde=inicio)                                   # cap. 14
    print(f"\n[log] {r['chamadas']} chamadas | {r['tokens_entrada']} tokens de entrada | "
          f"{r['tokens_saida']} de saída | {r['cache_lido']} do cache | "
          f"mais lenta {r['mais_lenta_ms']} ms | erros {r['erros']}")


if __name__ == "__main__":
    conn = conectar()                                                  # cap. 4
    carregar_manual(conn)
    if len(sys.argv) > 1:
        atender(conn, " ".join(sys.argv[1:]))
    else:
        while (texto := input("\nDescreva o problema (vazio para sair): ").strip()):
            atender(conn, texto)
