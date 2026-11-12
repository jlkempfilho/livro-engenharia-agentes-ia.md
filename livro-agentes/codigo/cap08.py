"""Capítulo 8 - saída estruturada: a resposta vira objeto validado."""
from triagem import triar

CHAMADOS = [
    "Bom dia, desde ontem ninguém do faturamento consegue emitir nota, dá erro de "
    "conexão com a SEFAZ. Estamos com 40 caminhões parados no pátio.",
    "Oi, queria saber como troco minha foto de perfil no sistema. Sem pressa.",
    "A impressora fiscal do caixa 3 está offline e o botão de reiniciar não resolveu.",
]

for texto in CHAMADOS:
    c = triar(texto)
    print(f"> {texto[:70]}...")
    print(f"  categoria={c.categoria} | prioridade={c.prioridade} | "
          f"precisa_humano={c.precisa_humano}")
    print(f"  resumo: {c.resumo}")
    print(f"  tipo Python: {type(c).__name__}\n")
