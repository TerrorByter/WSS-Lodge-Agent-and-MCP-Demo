"""The agents reach Claude through OpenRouter, configured only from OPENROUTER_* environment variables."""
import importlib, os, subprocess, sys
from pathlib import Path

import llm

ROOT = Path(__file__).parent


def load_llm(monkeypatch, **env):
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)   # hermetic: never read a real .env here
    for name in ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "OPENROUTER_BASE_URL"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    return importlib.reload(llm)


def test_key_is_sent_as_a_bearer_token_to_openrouter(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-stray")   # e.g. left over from another project
    m = load_llm(monkeypatch, OPENROUTER_API_KEY="sk-or-test")
    assert str(m.client.base_url) == "https://openrouter.ai/api/"
    assert m.client.auth_headers["Authorization"] == "Bearer sk-or-test"
    assert "sk-ant-stray" not in m.client.auth_headers.values()


def test_model_defaults_to_sonnet_and_can_be_overridden(monkeypatch):
    assert load_llm(monkeypatch).MODEL == "anthropic/claude-sonnet-4.6"
    assert load_llm(monkeypatch, OPENROUTER_MODEL="anthropic/claude-haiku-4.5").MODEL == "anthropic/claude-haiku-4.5"


def run_llm_in_copy(tmp_path, dotenv_text, **env):
    """Import a copy of llm.py that sits next to a .env we control; print the Authorization header and model."""
    (tmp_path / "llm.py").write_text((ROOT / "llm.py").read_text())
    (tmp_path / ".env").write_text(dotenv_text)
    clean = {k: v for k, v in os.environ.items() if not k.startswith(("OPENROUTER_", "ANTHROPIC_"))}
    code = "import llm; print(llm.client.auth_headers['Authorization'], llm.MODEL)"
    out = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env={**clean, **env}, check=True, capture_output=True, text=True)
    return out.stdout.split()


def test_key_and_model_are_read_from_the_dotenv_file(tmp_path):
    assert run_llm_in_copy(tmp_path, "OPENROUTER_API_KEY=sk-or-file\nOPENROUTER_MODEL=anthropic/claude-haiku-4.5\n") == [
        "Bearer", "sk-or-file", "anthropic/claude-haiku-4.5"]


def test_a_real_environment_variable_beats_the_dotenv_file(tmp_path):
    assert run_llm_in_copy(tmp_path, "OPENROUTER_API_KEY=sk-or-file\n", OPENROUTER_API_KEY="sk-or-env")[:2] == ["Bearer", "sk-or-env"]


def test_only_the_dotenv_next_to_llm_py_is_read_never_a_parent_folders(tmp_path):
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=sk-or-parent\n")   # e.g. a stray ~/.env
    project = tmp_path / "project"
    project.mkdir()
    (project / "llm.py").write_text((ROOT / "llm.py").read_text())
    clean = {k: v for k, v in os.environ.items() if not k.startswith(("OPENROUTER_", "ANTHROPIC_"))}
    code = "import llm; print(llm.client.auth_headers.get('Authorization'))"
    out = subprocess.run([sys.executable, "-c", code], cwd=project, env=clean, check=True, capture_output=True, text=True)
    assert "sk-or-parent" not in out.stdout


def test_both_agents_share_the_client_and_import_without_a_key():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("OPENROUTER_", "ANTHROPIC_"))}
    code = "import llm, mcp_agent, naive_agent; assert mcp_agent.client is naive_agent.client is llm.client"
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, check=True)
