"""llm.py - a única porta de saída para o modelo de linguagem.

Todo o resto do projeto fala com o modelo por aqui, num formato neutro.
Trocar de fornecedor é mudar a variável PROVEDOR, sem tocar nos outros arquivos.

Formato neutro das mensagens:
  {"role": "user", "content": "texto"}
  resposta.mensagem()                      -> turno do assistente
  {"role": "tool", "id": ..., "content": "texto", "erro": False}

Formato neutro das ferramentas:
  {"nome": ..., "descricao": ..., "parametros": <JSON Schema>}
"""
import json
import os
import time
from dataclasses import dataclass, field

import observa

PROVEDOR = os.getenv("PROVEDOR", "local")

PERFIS = {
    # Ollama rodando no Docker: gratuito, fala o dialeto OpenAI.
    "local": {
        "dialeto": "openai",
        "base_url": os.getenv("OLLAMA_URL", "http://ollama:11434") + "/v1",
        "chave": "ollama",
        "modelo": "qwen2.5:7b",
        "reserva": "qwen2.5:3b",
    },
    # Qualquer serviço que fale o dialeto OpenAI (OpenAI, Gemini, Groq, etc.).
    "compativel": {
        "dialeto": "openai",
        "base_url": os.getenv("BASE_URL"),
        "chave": os.getenv("CHAVE"),
        "modelo": None,
        "reserva": None,
    },
    # API da Anthropic (Claude): dialeto próprio.
    "anthropic": {
        "dialeto": "anthropic",
        "modelo": "claude-opus-5-5",
        "reserva": "claude-haiku-5-5",
    },
}
PERFIL = PERFIS[PROVEDOR]
MODELO = os.getenv("MODELO") or PERFIL["modelo"]
MODELO_RESERVA = os.getenv("MODELO_RESERVA") or PERFIL["reserva"]


class ErroDefinitivo(Exception):
    """Requisição errada (400) ou chave recusada (401, 403). Repetir não resolve."""


class ErroTemporario(Exception):
    """Limite de taxa, sobrecarga, rede ou modelo indisponível. Vale tentar o plano B."""


@dataclass
class Chamada:
    id: str
    nome: str
    args: dict


@dataclass
class Resposta:
    texto: str
    chamadas: list = field(default_factory=list)
    entrada: int = 0          # tokens de entrada
    saida: int = 0            # tokens de saída
    cache_lido: int = 0       # tokens de entrada lidos do cache (quando o fornecedor informa)
    parada: str = "fim"       # fim | ferramenta | limite | recusa
    modelo: str = ""
    ms: int = 0
    dados: object = None      # preenchido quando há esquema (saída estruturada)
    bruto: object = None      # conteúdo original do fornecedor

    def mensagem(self):
        return {"role": "assistant", "content": self.texto,
                "chamadas": self.chamadas, "_bruto": self.bruto}


def _esquema_estrito(esquema):
    """Fecha o JSON Schema: sem campos extras e com todos obrigatórios."""
    if isinstance(esquema, dict):
        if esquema.get("type") == "object":
            esquema["additionalProperties"] = False
            esquema["required"] = list(esquema.get("properties", {}))
        for valor in esquema.values():
            _esquema_estrito(valor)
    elif isinstance(esquema, list):
        for item in esquema:
            _esquema_estrito(item)
    return esquema


# ---------------------------------------------------------------- dialeto OpenAI
def _openai(mensagens, sistema, ferramentas, esquema, ao_texto, modelo, max_tokens):
    import openai
    cliente = openai.OpenAI(base_url=PERFIL["base_url"], api_key=PERFIL["chave"], max_retries=2)

    msgs = [{"role": "system", "content": sistema}] if sistema else []
    for m in mensagens:
        if m["role"] == "tool":
            msgs.append({"role": "tool", "tool_call_id": m["id"], "content": m["content"]})
        elif m["role"] == "assistant":
            bruto = m.get("_bruto")
            if isinstance(bruto, dict):
                # Turno deste dialeto: volta exatamente como veio. Há fornecedor que só
                # reconhece a própria chamada de ferramenta se os argumentos voltarem
                # byte a byte iguais, e que exige de volta o campo de raciocínio.
                msgs.append(bruto)
                continue
            novo = {"role": "assistant", "content": m["content"] or None}
            if m.get("chamadas"):   # turno vindo de outro dialeto: remonta
                novo["tool_calls"] = [
                    {"id": c.id, "type": "function",
                     "function": {"name": c.nome, "arguments": json.dumps(c.args)}}
                    for c in m["chamadas"]]
            msgs.append(novo)
        else:
            msgs.append({"role": "user", "content": m["content"]})

    extras = {}
    if ferramentas:
        extras["tools"] = [
            {"type": "function", "function": {
                "name": f["nome"], "description": f["descricao"],
                "parameters": f["parametros"], "strict": True}}
            for f in ferramentas]
    if esquema:
        extras["response_format"] = {"type": "json_schema", "json_schema": {
            "name": esquema.__name__, "strict": True,
            "schema": _esquema_estrito(esquema.model_json_schema())}}

    try:
        if ao_texto:
            texto, uso, fim, parciais = "", None, "stop", {}
            fluxo = cliente.chat.completions.create(
                model=modelo, messages=msgs, max_tokens=max_tokens, stream=True,
                stream_options={"include_usage": True}, **extras)
            for evento in fluxo:
                uso = evento.usage or uso
                if not evento.choices:
                    continue
                escolha = evento.choices[0]
                fim = escolha.finish_reason or fim
                if escolha.delta.content:
                    texto += escolha.delta.content
                    ao_texto(escolha.delta.content)
                for t in escolha.delta.tool_calls or []:
                    p = parciais.setdefault(t.index, {"id": "", "nome": "", "args": ""})
                    p["id"] = t.id or p["id"]
                    p["nome"] = (t.function.name or "") or p["nome"]
                    p["args"] += t.function.arguments or ""
            chamadas = [Chamada(p["id"], p["nome"], json.loads(p["args"] or "{}"))
                        for p in parciais.values()]
            bruto = {"role": "assistant", "content": texto or None}
            if parciais:
                bruto["tool_calls"] = [
                    {"id": p["id"], "type": "function",
                     "function": {"name": p["nome"], "arguments": p["args"] or "{}"}}
                    for p in parciais.values()]
        else:
            r = cliente.chat.completions.create(
                model=modelo, messages=msgs, max_tokens=max_tokens, **extras)
            escolha, uso = r.choices[0], r.usage
            texto, fim = escolha.message.content or "", escolha.finish_reason
            chamadas = [Chamada(t.id, t.function.name, json.loads(t.function.arguments or "{}"))
                        for t in escolha.message.tool_calls or []]
            bruto = escolha.message.model_dump(exclude_none=True)
    except (openai.BadRequestError, openai.AuthenticationError,
            openai.PermissionDeniedError) as e:      # 400, 401, 403: erro nosso
        raise ErroDefinitivo(str(e)) from e
    except openai.OpenAIError as e:
        raise ErroTemporario(f"{type(e).__name__}: {e}") from e

    detalhes = getattr(uso, "prompt_tokens_details", None)
    parada = "ferramenta" if chamadas else {"length": "limite",
                                            "content_filter": "recusa"}.get(fim, "fim")
    return Resposta(texto=texto, chamadas=chamadas,
                    entrada=uso.prompt_tokens if uso else 0,
                    saida=uso.completion_tokens if uso else 0,
                    cache_lido=getattr(detalhes, "cached_tokens", 0) or 0,
                    parada=parada, modelo=modelo, bruto=bruto)


# ------------------------------------------------------------- dialeto Anthropic
def _anthropic(mensagens, sistema, ferramentas, esquema, ao_texto, modelo, max_tokens):
    import anthropic
    cliente = anthropic.Anthropic(max_retries=2)

    msgs = []
    for m in mensagens:
        if m["role"] == "tool":
            bloco = {"type": "tool_result", "tool_use_id": m["id"],
                     "content": m["content"], "is_error": bool(m.get("erro"))}
            # resultados da mesma volta vão juntos, numa única mensagem de usuário
            if msgs and msgs[-1]["role"] == "user" and isinstance(msgs[-1]["content"], list):
                msgs[-1]["content"].append(bloco)
            else:
                msgs.append({"role": "user", "content": [bloco]})
        elif m["role"] == "assistant":
            conteudo = m.get("_bruto")
            if not isinstance(conteudo, list):  # turno de outro dialeto: remonta os blocos
                conteudo = ([{"type": "text", "text": m["content"]}] if m["content"] else []) + [
                    {"type": "tool_use", "id": c.id, "name": c.nome, "input": c.args}
                    for c in m.get("chamadas", [])]
            msgs.append({"role": "assistant", "content": conteudo})
        else:
            msgs.append({"role": "user", "content": m["content"]})

    args = {"model": modelo, "max_tokens": max_tokens, "messages": msgs,
            "output_config": {"effort": "low"},
            "cache_control": {"type": "ephemeral"}}   # cache automático do prefixo
    if sistema:
        # Ponto de cache próprio no fim do sistema: perguntas diferentes reaproveitam
        # o prefixo (ferramentas + sistema). O cache automático cobre a conversa.
        args["system"] = [{"type": "text", "text": sistema,
                           "cache_control": {"type": "ephemeral"}}]
    if ferramentas:
        args["tools"] = [{"name": f["nome"], "description": f["descricao"],
                          "input_schema": f["parametros"], "strict": True}
                         for f in ferramentas]
    if esquema:
        args["output_config"]["format"] = {
            "type": "json_schema", "schema": _esquema_estrito(esquema.model_json_schema())}

    try:
        if ao_texto:
            with cliente.messages.stream(**args) as fluxo:
                for pedaco in fluxo.text_stream:
                    ao_texto(pedaco)
                r = fluxo.get_final_message()
        else:
            r = cliente.messages.create(**args)
    except (anthropic.BadRequestError, anthropic.AuthenticationError,
            anthropic.PermissionDeniedError) as e:   # 400, 401, 403: erro nosso
        raise ErroDefinitivo(str(e)) from e
    except anthropic.AnthropicError as e:
        raise ErroTemporario(f"{type(e).__name__}: {e}") from e

    lido = r.usage.cache_read_input_tokens or 0
    chamadas = [Chamada(b.id, b.name, b.input) for b in r.content if b.type == "tool_use"]
    parada = {"tool_use": "ferramenta", "max_tokens": "limite",
              "refusal": "recusa"}.get(r.stop_reason, "fim")
    return Resposta(texto="".join(b.text for b in r.content if b.type == "text"),
                    chamadas=chamadas,
                    # Aqui input_tokens NÃO inclui o que foi para o cache nem o que veio
                    # dele. Somamos os três para "entrada" significar o mesmo que no
                    # dialeto OpenAI: todos os tokens de entrada da chamada.
                    entrada=(r.usage.input_tokens + lido
                             + (r.usage.cache_creation_input_tokens or 0)),
                    saida=r.usage.output_tokens, cache_lido=lido,
                    parada=parada, modelo=modelo, bruto=r.content)


_DIALETOS = {"openai": _openai, "anthropic": _anthropic}


# ------------------------------------------------------------------ porta única
def conversar(mensagens, sistema=None, ferramentas=None, esquema=None,
              ao_texto=None, modelo=None, max_tokens=2000, etapa="geral", _tentativa=1):
    """Uma chamada ao modelo. Devolve uma Resposta no formato neutro.

    esquema  : classe Pydantic; a resposta volta validada em resposta.dados (cap. 8)
    ao_texto : função chamada a cada pedaço de texto, para streaming (cap. 9)
    etapa    : rótulo que vai para o log de observabilidade (cap. 14)
    """
    modelo = modelo or MODELO
    inicio = time.time()
    registro = {"etapa": etapa, "provedor": PROVEDOR, "modelo": modelo}
    try:
        r = _DIALETOS[PERFIL["dialeto"]](mensagens, sistema, ferramentas, esquema,
                                         ao_texto, modelo, max_tokens)
    except (ErroDefinitivo, ErroTemporario) as e:
        observa.registrar({**registro, "ms": round((time.time() - inicio) * 1000),
                           "erro": type(e).__name__})
        raise
    r.ms = round((time.time() - inicio) * 1000)
    observa.registrar({**registro, "ms": r.ms, "entrada": r.entrada, "saida": r.saida,
                       "cache_lido": r.cache_lido, "parada": r.parada,
                       "ferramentas": [c.nome for c in r.chamadas]})
    if esquema:
        # Formato garantido não é resposta garantida: o modelo pode ser cortado pelo
        # limite de tokens no meio do JSON. Uma nova tentativa; depois, erro explícito.
        try:
            if r.parada != "fim":
                raise ValueError(f"parada={r.parada}")
            r.dados = esquema.model_validate_json(r.texto)
        except ValueError as e:
            if _tentativa >= 2:
                raise ErroTemporario(f"saída estruturada inválida: {e}") from e
            return conversar(mensagens, sistema, ferramentas, esquema, ao_texto, modelo,
                             max_tokens, etapa, _tentativa=_tentativa + 1)
    return r


def conversar_com_reserva(mensagens, **opcoes):
    """Tenta o modelo principal e, se ele falhar por erro temporário, o reserva (cap. 12)."""
    modelos = [opcoes.pop("modelo", None) or MODELO, MODELO_RESERVA]
    ultimo = None
    for modelo in [m for m in modelos if m]:
        try:
            return conversar(mensagens, modelo=modelo, **opcoes)
        except ErroTemporario as e:
            ultimo = e
            print(f"  [plano B] {modelo} falhou: {str(e)[:80]}")
    raise ErroTemporario(f"todos os modelos falharam: {ultimo}")
