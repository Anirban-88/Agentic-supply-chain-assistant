# GitHub Copilot / AI Agent Instructions for this Repository

Purpose: make an AI-assistant productive immediately in this codebase by documenting architecture, developer workflows, conventions, and concrete examples.

## Quick Architecture Snapshot
- High-level: Streamlit UI -> Orchestrator -> specialized Agents -> Neo4j KG (LLM assists agents).
- Primary directories:
  - `agents/` — Agent implementations and `Orchestrator` (`agents/orchestrator.py`).
  - `mcp_servers/` — Thin HTTP wrappers for agents: `/query`, `/health`, `/capabilities`.
  - `llm/` — `LlamaClient` (model loading, prompts, helpers like `extract_entity`, `summarize_results`).
  - `database/` — `neo4j_connector.py` (singleton connector, `execute_query`, `get_schema`).
  - `ui/` — `streamlit_app.py` (toggle between MCP servers and in-process orchestrator).
  - `config/` — All runtime/config knobs (ports, thresholds, keywords, logging).

## Key Runtime Commands (examples)
- Start Neo4j (via Docker Compose):
  - `docker-compose up -d`
- Start distributed MCP servers (recommended for integration):
  - `python scripts/10_start_mcp_servers.py --subprocess`
  - This starts agent servers first and the orchestrator last (see `scripts/10_start_mcp_servers.py`).
- Run Streamlit UI locally:
  - `streamlit run ui/streamlit_app.py`
  - Toggle `Use MCP Servers` in the sidebar or set `USE_MCP_SERVERS=false` env to use in-process mode.
- Run test / helpers:
  - `python scripts/11_test_agents.py` — unit/integration checks for agents
  - `python scripts/12_test_distributed_orchestrator.py` — distributed orchestration tests
  - `python scripts/01_generate_data.py` — generate synthetic data for Neo4j

## Important Environment Variables / Config
- `.env` is consumed via `python-dotenv` in multiple configs. Important keys:
  - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — Neo4j connection
  - `HUGGINGFACE_TOKEN` — optional, required for some models
  - `USE_MCP_SERVERS` — toggles Streamlit to call the external MCP orchestrator
  - `ORCHESTRATOR_URL` — default `http://localhost:8000`
- Config files to modify rather than hard-coding: `config/*.py` (e.g. `mcp_config.py`, `neo4j_config.py`, `agent_config.py`).

## Agent Conventions (follow these to add/modify agents)
- Base class: `agents/base_agent.py`
  - Required methods: `can_handle(query: str) -> float` and `process(query: str) -> Dict`
  - Use `self.execute_cypher(cypher, params)` for DB access (returns list of dicts).
  - Use `self.format_response(...)` and `self.format_error(...)` for consistent return shapes.
  - LLM helpers are available via `self.llm` (singleton `get_llama_client()`)
- Typical return structure for success:
  - `{ 'agent': <name>, 'status': 'success', 'data': [...], 'summary': '...', 'record_count': N }`
- `can_handle` uses keyword-count heuristic (keywords defined on the agent) and returns confidence [0.0, 1.0].
- To register a new agent locally:
  1. Create `agents/<your_agent>.py` subclassing `BaseAgent`.
  2. Add the agent to `Orchestrator.__init__` list or update `config/agent_config.py` keywords.
  3. If exposing it as an MCP server, add server `mcp_servers/<your_agent>_server.py` similar to existing ones and add config to `MCP_SERVERS` in `config/mcp_config.py`.

## Orchestrator Behavior Notes
- File: `agents/orchestrator.py`
  - Uses `agent.can_handle(query)` to select agents (threshold from `config/agent_config.ORCHESTRATOR_CONFIG['confidence_threshold']`).
  - `max_agents_per_query` limits parallelism.
  - When no agent matches, orchestrator uses the LLM to produce a helpful `no_agent` response.
  - Aggregation: single-agent responses are formatted differently from multi-agent results (see `_format_multi_response`).

## MCP Server HTTP Contract
- Endpoints:
  - `GET /health` → returns `{ status: 'healthy', agent: <name>, version: '0.1.0' }`
  - `GET /capabilities` → returns `name, description, keywords, endpoints`
  - `POST /query` → accepts `{ "query": "..." }`; responds `{ 'agent': ..., 'query': ..., 'result': <agent result> }`
- Streamlit expects the top-level orchestrator response to include a `result` field when calling `ORCHESTRATOR_URL/query`.

## LLM & Prompting Patterns
- `llm/llama_client.py` contains helpers used widely:
  - `extract_entity(query, 'product name')` — returns a raw string used in cypher params
  - `summarize_results(query, results)` — summarize top-N results (default N=5)
  - `generate_cypher(query, schema)` — returns a generated cypher snippet
- Note: LLM calls are treated as synchronous blocking calls and can be costly — cache or short-circuit for simple queries when possible.

## Debugging / Local Development Tips
- To debug an agent in-process: set `USE_MCP_SERVERS=false` and use Streamlit or call `get_orchestrator()` from a Python REPL.
- To debug server processes: run `python mcp_servers/<agent>_server.py --port <port>` directly (no subprocess manager).
- Logs are placed under `logs/` and configured via `config/logging_config.py`.
- Neo4j schema helper: `database/neo4j_connector.py.get_schema()` for prompt contexts when generating Cypher.

## Tests & Expected Failures
- Tests are script-based under `scripts/` (not pytest): review `scripts/11_test_agents.py` and `scripts/12_test_distributed_orchestrator.py` for examples of expected requests and responses.
- Common failure modes to surface in PRs:
  - Missing `HUGGINGFACE_TOKEN` or local GPU drivers → model load errors
  - Neo4j connection/auth errors → ensure `NEO4J_PASSWORD` is correct and Docker container is running
  - Timeout errors when LLM or complex Cypher queries exceed configured timeouts

## Additions / PR Guidance
- Keep agent `process()` idempotent and side-effect free where possible (agents should query and summarize, not mutate data).
- Use `execute_cypher` for DB reads; if writes are added, follow existing connector patterns and add tests in `scripts/`.
- Update `config/agent_config.py` and `config/mcp_config.py` when adding/removing agents or changing ports.

---
If anything is unclear or you'd like more examples (e.g. a minimal sample agent implementation or an MCP client snippet), tell me which area to expand and I will iterate. ✅