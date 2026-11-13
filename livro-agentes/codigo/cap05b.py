"""Capítulo 5, parte 2 - medir a busca: só significado x híbrida (significado + palavra)."""
from banco import buscar, buscar_hibrida, carregar_manual, conectar

# (pergunta, pedaço que identifica o trecho correto)
CASOS = [
    ("como libero um pedido bloqueado por crédito?", "Liberação de Crédito"),
    ("onde emito nota fiscal de saída?", "Documento de Saída"),
    ("o que o cadastro de produto exige?", "armazém padrão"),
    ("até quando posso cancelar uma nota?", "24 horas"),
    ("que horas roda o backup?", "às 2h"),
    ("esqueci minha senha do sistema", "Redefinir Senha"),
    ("preciso de acesso remoto de casa", "VPN"),
    ("a nota não transmite", "certificado digital"),
    ("o que é a rejeição 204?", "Rejeição 204"),
    ("deu rejeição 539 na nota", "Rejeição 539"),
    ("erro 778 ao transmitir", "Rejeição 778"),
    ("nota rejeitada com código 539", "Rejeição 539"),
]


def medir(conn, nome, funcao):
    top1 = top3 = 0
    erros = []
    for pergunta, marca in CASOS:
        achados = [c for c, _, _ in funcao(conn, pergunta, k=3)]
        top1 += bool(achados) and marca in achados[0]
        top3 += any(marca in c for c in achados)
        if not (achados and marca in achados[0]):
            erros.append(f"{pergunta}  ->  veio: {achados[0][:45] if achados else 'nada'}...")
    print(f"=== {nome} ===")
    print(f"  trecho certo em 1º lugar: {top1}/{len(CASOS)} | entre os 3 primeiros: {top3}/{len(CASOS)}")
    for e in erros:
        print(f"  errou o 1º lugar: {e}")
    print()


if __name__ == "__main__":
    conn = conectar()
    carregar_manual(conn)
    medir(conn, "só significado (vetorial)", buscar)
    medir(conn, "híbrida (vetorial + palavra-chave, fusão RRF)", buscar_hibrida)
