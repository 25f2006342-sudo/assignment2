# Live MCP Challenge Server

Minimal Flask-based MCP JSON-RPC server for the live challenge task.

## Render settings
- Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Endpoint to submit: `https://YOUR-SERVICE.onrender.com/mcp`

Optional environment variable:
- `EXAM_EMAIL=25f2006342@ds.study.iitm.ac.in`

The server exposes exactly one tool: `solve_challenge`. For every `tools/call`, it reads `X-Exam-Challenge` from the HTTP request headers and returns the first 16 lowercase hex characters of SHA-256 of `challenge:normalized_email`.
