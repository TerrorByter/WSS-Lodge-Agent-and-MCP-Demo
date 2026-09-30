# Agents + MCP workshop

Open `agents_and_mcp_demo.ipynb` and run it top to bottom. You need Python 3.10+ and an [OpenRouter](https://openrouter.ai) API key. Claude is reached through OpenRouter.

## Setup (once)

**1. Add your key.** Copy `.env.example` to `.env`, open it and paste your OpenRouter key after `OPENROUTER_API_KEY=`. Files starting with a dot are hidden in Finder and File Explorer; VS Code shows them.

```bash
cp .env.example .env        # macOS / Linux
```

```powershell
copy .env.example .env      # Windows (PowerShell)
```

Never share your `.env` or commit it (it is already in `.gitignore`). A real environment variable named `OPENROUTER_API_KEY`, if you have one, takes precedence over the file. With neither, the notebook asks for the key in its second code cell and keeps it in memory only.

Optional: set `OPENROUTER_MODEL` in `.env` to pick another Claude model (default `anthropic/claude-sonnet-4.6`; slugs at [openrouter.ai/models](https://openrouter.ai/models)).

**2. Create a virtual environment** so the pinned packages don't touch your other projects.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install jupyterlab
jupyter lab
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install jupyterlab
jupyter lab
```

Using VS Code instead? Install the Python and Jupyter extensions, open this folder, open the notebook and pick the `.venv` kernel (VS Code offers to install `ipykernel`).

The first notebook cell installs `anthropic`, `mcp` and `python-dotenv` from `requirements.txt` into the kernel's environment, and checks that you opened the notebook from this folder.

## Files

| File | Role |
|---|---|
| `airlines.py` | Three fake airline APIs, each with its own shape |
| `llm.py` | The one Claude client both agents share, pointed at OpenRouter; reads your key from `.env` |
| `.env.example` | Template for your `.env` (your real `.env` stays private) |
| `naive_agent.py` | Before MCP: one hand-written tool per airline |
| `flight_mcp_server.py` | The MCP server: one interface in front of all three |
| `mcp_agent.py` | With MCP: discovers tools from a config and runs the agent loop |
| `mcp_config.json`, `http_config.json`, `empty_config.json` | Which MCP servers the agent connects to |
| `test_mcp_transports.py`, `test_llm.py` | `pytest` checks for the server (stdio and HTTP) and the OpenRouter client config (no API key needed) |

## Troubleshooting

- **`Open this notebook from the project folder`**: the notebook must sit next to `mcp_config.json`. Open the folder, not just the file.
- **`Could not resolve authentication method`**: no key was found. Check that `.env` sits next to the notebook, that the line reads `OPENROUTER_API_KEY=sk-or-...` (no quotes, no spaces), then restart the kernel: it reads `.env` only once, at startup.
- **`401 ... User not found`**: OpenRouter doesn't recognise the key. Check it was copied whole (it starts with `sk-or-`).
- **`Port 8765 is already in use`** (Part 8): change the port in `http_config.json`.
- **`No module named pip`**: create the venv with `python -m venv` (a `uv venv` needs `--seed`).
