import json
from flask import Flask, request, jsonify, Response, stream_with_context
import requests

app = Flask(__name__)

# === CONFIG ===
API_KEY = "0815e928642441bd9aa4b3e670c8fa80"  # sua chave Base44
BASE_URL = "https://app.base44.com/api/apps/680d6ca95153f09fa29b4f1a/entities"

COMMON_HEADERS = {
    "api_key": API_KEY,
    "Content-Type": "application/json"
}

# --- Definição das ferramentas ---
TOOLS = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM (filtro por nome opcional)",
        "inputSchema": {"type": "object","properties": {"name": {"type": "string"}}}
    },
    {
        "name": "atualizarCliente",
        "description": "Atualiza um cliente no CRM. Ex: status, phone, notes etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "dados": {"type": "object"}
            },
            "required": ["id", "dados"]
        }
    },
    {
        "name": "consultarInteracoes",
        "description": "Lista interações. Filtro por client_id opcional",
        "inputSchema": {"type": "object","properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarTarefas",
        "description": "Lista tarefas. Filtro por client_id opcional",
        "inputSchema": {"type": "object","properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarVisitas",
        "description": "Lista visitas. Filtro por client_id opcional",
        "inputSchema": {"type": "object","properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarContatosLoja",
        "description": "Lista contatos de loja. Filtro por client_id opcional",
        "inputSchema": {"type": "object","properties": {"client_id": {"type": "string"}}}
    }
]

# === Funções auxiliares ===
def b44_get(entity: str, params=None):
    url = f"{BASE_URL}/{entity}"
    r = requests.get(url, headers=COMMON_HEADERS, params=params or {})
    r.raise_for_status()
    return r.json()

def b44_put(entity: str, entity_id: str, payload: dict):
    url = f"{BASE_URL}/{entity}/{entity_id}"
    r = requests.put(url, headers=COMMON_HEADERS, json=payload or {})
    r.raise_for_status()
    return r.json()

# === Implementações das ferramentas ===
def tool_consultar_clientes(arguments: dict):
    name = arguments.get("name")
    params = {"name": name} if name else {}
    return b44_get("Client", params)

def tool_atualizar_cliente(arguments: dict):
    entity_id = arguments.get("id")
    dados = arguments.get("dados") or {}
    if not entity_id:
        raise ValueError("Parâmetro 'id' é obrigatório")
    return b44_put("Client", entity_id, dados)

def tool_consultar_interacoes(arguments: dict):
    client_id = arguments.get("client_id")
    params = {"client_id": client_id} if client_id else {}
    return b44_get("Interaction", params)

def tool_consultar_tarefas(arguments: dict):
    client_id = arguments.get("client_id")
    params = {"client_id": client_id} if client_id else {}
    try:
        return b44_get("Task", params)   # tenta Task
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return b44_get("Interaction", params)  # fallback
        raise

def tool_consultar_visitas(arguments: dict):
    client_id = arguments.get("client_id")
    params = {"client_id": client_id} if client_id else {}
    return b44_get("Visit", params)

def tool_consultar_contatos_loja(arguments: dict):
    client_id = arguments.get("client_id")
    params = {"client_id": client_id} if client_id else {}
    return b44_get("ContatoLoja", params)

TOOL_IMPL = {
    "consultarClientes": tool_consultar_clientes,
    "atualizarCliente": tool_atualizar_cliente,
    "consultarInteracoes": tool_consultar_interacoes,
    "consultarTarefas": tool_consultar_tarefas,
    "consultarVisitas": tool_consultar_visitas,
    "consultarContatosLoja": tool_consultar_contatos_loja,
}

# === ENDPOINTS MCP ===

# Agora /sse responde a POST (como o ChatGPT espera)
@app.post("/sse")
def sse():
    def generate():
        base = request.headers.get("X-Forwarded-Proto", request.scheme) + "://" + request.headers.get("X-Forwarded-Host", request.host)
        message_url = f"{base}/messages"
        # evento endpoint
        yield f"event: endpoint\n"
        yield f"data: {json.dumps({'type':'endpoint','message_url':message_url})}\n\n"
        # server_info com ferramentas
        yield f"event: message\n"
        yield f"data: {json.dumps({'type':'server_info','tools':TOOLS})}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.post("/messages")
def messages():
    payload = request.get_json(force=True, silent=False) or {}
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}
    try:
        if method == "tools/list":
            return jsonify({"id": req_id, "result": {"tools": TOOLS}})
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if name not in TOOL_IMPL:
                return jsonify({"id": req_id, "error": {"code": 404, "message": f"tool '{name}' not found"}}), 404
            result = TOOL_IMPL[name](arguments)
            return jsonify({"id": req_id, "result": {"content": result}})
        if method in ("ping", "health"):
            return jsonify({"id": req_id, "result": "ok"})
        return jsonify({"id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}}), 400
    except Exception as e:
        return jsonify({"id": req_id, "error": {"code": 500, "message": str(e)}}), 500

@app.get("/")
def index():
    return "MCP server do CRM Base44 está no ar. Use /sse e /messages."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
