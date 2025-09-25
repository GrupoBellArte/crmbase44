from flask import Flask, request, Response, jsonify, stream_with_context
import json
import os

app = Flask(__name__)

# --- Definição de ferramentas (MCP Tools) ---
TOOLS = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "ID do cliente"},
                "dados": {"type": "object", "description": "Filtros adicionais"}
            }
        }
    },
    {
        "name": "atualizarCliente",
        "description": "Atualiza um cliente no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "dados": {"type": "object"}
            },
            "required": ["id", "dados"]
        }
    }
]

SERVER_NAME = "CRM Base44 MCP"
SERVER_VERSION = "1.0.0"
DEFAULT_PROTOCOL = "2025-06-18"  # compat com clientes atuais

# --- Helpers JSON-RPC ---
def rpc_ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

def rpc_err(req_id, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}

def get_base_url():
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    host = request.headers.get("X-Forwarded-Host", request.host)
    return f"{proto}://{host}"

# === ENDPOINTS MCP (HTTP+SSE “antigo”) ===
# /sse: SOMENTE GET. O cliente abrirá um EventSource e lerá o `endpoint`.
@app.get("/sse")
def sse():
    def generate():
        message_url = f"{get_base_url()}/messages"
        # O payload do evento `endpoint` deve ser uma STRING com a URI do endpoint de mensagens
        # (não um JSON). Depois disso, podemos manter a conexão aberta/quieta.
        yield "event: endpoint\n"
        yield f"data: {message_url}\n\n"
        # (Opcional) keep-alive ping a cada 25s para proxies não derrubarem a conexão
        # while True:
        #     yield ": keep-alive\n\n"
        #     time.sleep(25)
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    return Response(stream_with_context(generate()), mimetype="text/event-stream", headers=headers)

# /messages: recebe JSON-RPC do cliente
@app.post("/messages")
def messages():
    try:
        data = request.get_json(silent=True) or {}
        # Notificações (sem id) => 202 Accepted sem corpo (conforme Streamable HTTP; serve aqui também)
        # mas o ChatGPT deve enviar Requests com id.
        req_id = data.get("id")
        method = data.get("method")
        params = data.get("params") or {}

        # Falta id/method => erro JSON-RPC
        if not method or req_id is None:
            return jsonify(rpc_err(req_id, -32600, "Invalid Request")), 200

        # --- MÉTODOS SUPORTADOS ---

        # initialize (handshake)
        if method == "initialize":
            client_proto = (params.get("protocolVersion") or DEFAULT_PROTOCOL)
            result = {
                "protocolVersion": client_proto,
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "capabilities": {
                    "tools": {
                        # envie true se seu servidor emitir notifications/tools/list_changed
                        "listChanged": False
                    }
                },
                # Instruções ajudam o modelo a entender os recursos do servidor
                "instructions": "Ferramentas disponíveis: consultarClientes, atualizarCliente."
            }
            return jsonify(rpc_ok(req_id, result)), 200

        # tools/list
        if method == "tools/list":
            result = {"tools": TOOLS}
            return jsonify(rpc_ok(req_id, result)), 200

        # tools/call
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Aqui você chamaria seu CRM de fato. Vamos simular.
            text = f"Tool '{tool_name}' chamada com argumentos: {json.dumps(arguments, ensure_ascii=False)}"
            result = {
                "content": [
                    {"type": "text", "text": text}
                ],
                "isError": False
            }
            return jsonify(rpc_ok(req_id, result)), 200

        # ping
        if method == "ping":
            return jsonify(rpc_ok(req_id, {"status": "ok"})), 200

        # Método desconhecido -> erro JSON-RPC, mas HTTP 200
        return jsonify(rpc_err(req_id, -32601, f"Method '{method}' not found")), 200

    except Exception as e:
        # Nunca retornar 500 bruto para o cliente MCP; encapsule em erro JSON-RPC
        # mas mantenha HTTP 200 para não quebrar o handshake do cliente.
        req_id = None
        try:
            body = request.get_json(silent=True) or {}
            req_id = body.get("id")
        except Exception:
            pass
        return jsonify(rpc_err(req_id, -32603, "Internal error", str(e))), 200

@app.get("/")
def home():
    return "MCP do CRM Base44 no ar. Use /sse (GET) e /messages (POST)."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
