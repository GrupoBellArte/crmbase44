from flask import Flask, request, Response, jsonify, stream_with_context
import json

app = Flask(__name__)

# Ferramentas disponíveis
TOOLS = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "dados": {"type": "object"}
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

# === ENDPOINTS MCP ===

# /sse deve responder tanto GET quanto POST
@app.route("/sse", methods=["GET", "POST"])
def sse():
    def generate():
        base = request.headers.get("X-Forwarded-Proto", request.scheme) + "://" + request.headers.get("X-Forwarded-Host", request.host)
        message_url = f"{base}/messages"

        # evento endpoint
        yield f"event: endpoint\n"
        yield f"data: {json.dumps({'type': 'endpoint', 'message_url': message_url})}\n\n"

        # server_info com ferramentas
        yield f"event: message\n"
        yield f"data: {json.dumps({'type': 'server_info', 'tools': TOOLS})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


# /messages recebe as chamadas do ChatGPT
@app.route("/messages", methods=["POST"])
def messages():
    try:
        data = request.json or {}
        req_id = data.get("id")
        method = data.get("method")
        params = data.get("params") or {}

        # Lista ferramentas
        if method == "tools/list":
            return jsonify({"id": req_id, "result": {"tools": TOOLS}})

        # Chamada de ferramenta
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return jsonify({
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": f"Tool '{tool_name}' chamada com argumentos: {arguments}"}
                    ]
                }
            })

        # Healthcheck
        if method in ("ping", "health"):
            return jsonify({"id": req_id, "result": "ok"})

        return jsonify({"id": req_id, "error": {"code": -32601, "message": f"Method '{method}' não suportado"}}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Página inicial
@app.route("/")
def home():
    return "MCP server do CRM Base44 está no ar. Use /sse e /messages."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
