"""Capítulo 12 - fallback: o usuário nunca vê um stack trace."""
import llm
from llm import ErroDefinitivo, ErroTemporario, conversar, conversar_com_reserva

PERGUNTA = [{"role": "user", "content": "Diga 'sistema no ar' e nada mais."}]


def atender(**opcoes):
    try:
        r = conversar_com_reserva(PERGUNTA, etapa="cap12", **opcoes)
        return f"{r.texto.strip()}  [respondido por: {r.modelo}]"
    except ErroTemporario:
        return "Assistente indisponível no momento. Abra um chamado pelo portal."
    except ErroDefinitivo as e:
        return f"Erro de requisição (corrigir o código, não repetir): {str(e)[:120]}"


print("1. tudo normal:")
print("  ", atender())

print("\n2. modelo principal fora do ar (nome inexistente):")
print("  ", atender(modelo="modelo-que-nao-existe"))

print("\n3. principal e reserva fora do ar:")
reserva_original, llm.MODELO_RESERVA = llm.MODELO_RESERVA, "reserva-que-nao-existe"
print("  ", atender(modelo="modelo-que-nao-existe"))
llm.MODELO_RESERVA = reserva_original

print("\n4. requisição errada (erro nosso): não vai para o plano B")
try:
    conversar([], etapa="cap12")          # conversa sem nenhuma mensagem
    print("   (este provedor aceitou o valor inválido)")
except ErroDefinitivo as e:
    print("   ErroDefinitivo:", str(e)[:120])
except ErroTemporario as e:
    print("   ErroTemporario:", str(e)[:120])
