import hashlib
import os
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

EMAIL = os.environ.get("EXAM_EMAIL", "25f2006342@ds.study.iitm.ac.in").strip().lower()
PROTOCOL_VERSION = "2025-03-26"
SERVER_INFO = {"name": "live-challenge-server", "version": "1.0.0"}

def jsonrpc_result(req_id, result):
    return jsonify({"jsonrpc": "2.0", "id": req_id, "result": result})

def jsonrpc_error(req_id, code, message):
    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

@app.route("/", methods=["GET"])
def root():
    return jsonify({"service": "Live MCP challenge server", "endpoint": "/mcp"})

@app.route("/mcp", methods=["GET", "DELETE"])
def mcp_non_post():
    # This minimal server uses JSON responses to POST requests.
    if request.method == "GET":
        return make_response("MCP endpoint. Send JSON-RPC POST requests.", 200)
    return make_response("", 405)

@app.route("/mcp", methods=["POST"])
def mcp_post():
    payload = request.get_json(silent=True) or {}
    method = payload.get("method", "")
    req_id = payload.get("id")

    # Notifications have no id and should not receive a JSON-RPC result.
    if method == "notifications/initialized" or method.startswith("notifications/"):
        return make_response("", 202)

    if method == "initialize":
        params = payload.get("params") or {}
        requested_version = params.get("protocolVersion", PROTOCOL_VERSION)
        return jsonrpc_result(req_id, {
            "protocolVersion": requested_version,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO
        })

    if method == "ping":
        return jsonrpc_result(req_id, {})

    if method == "tools/list":
        return jsonrpc_result(req_id, {
            "tools": [{
                "name": "solve_challenge",
                "description": "Return the challenge-specific verification text from the X-Exam-Challenge HTTP header.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }]
        })

    if method == "tools/call":
        params = payload.get("params") or {}
        tool_name = params.get("name")
        if tool_name != "solve_challenge":
            return jsonrpc_error(req_id, -32602, "Unknown tool")
        challenge = request.headers.get("X-Exam-Challenge", "")
        if not challenge:
            return jsonrpc_result(req_id, {
                "content": [{"type": "text", "text": "missing-challenge"}],
                "isError": True
            })
        digest = hashlib.sha256(f"{challenge}:{EMAIL}".encode("utf-8")).hexdigest()[:16]
        return jsonrpc_result(req_id, {
            "content": [{"type": "text", "text": digest}]
        })

    return jsonrpc_error(req_id, -32601, "Method not found")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
