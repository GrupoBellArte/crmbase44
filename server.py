from flask import Flask, request, Response, jsonify
import json

app = Flask(__name__)

# Definição das ferramentas disponíveis
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
            }
        }
    }
]

# SSE compatível com GET e POST
@app.route("/sse", methods=["GET", "POST"])
def sse():
    try:
        def event_stream():
            yield f"event: tool_list\n"
            yield f"data: {json.dumps({'tools': TOOLS})}\n\n"

        return Response(event_stream(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para ChatGPT enviar ações
@app.route("/messages", methods=["POST"])
def messages():
    try:
        data = request.json
        print("Mensagem recebida:", json.dumps(data, indent=2))

        tool_name = data.get("tool", "desconhecido")
        arguments = data.get("arguments", {})

        resposta = {
            "content": [
                {
                    "type": "text",
                    "text": f"A ferramenta '{tool_name}' foi chamada com os argumentos: {arguments}"
                }
            ]
        }
        return jsonify(resposta)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Página inicial
@app.route("/")
def home():
    return "MCP server do CRM Base44 está no ar. Use /sse e /messages."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
