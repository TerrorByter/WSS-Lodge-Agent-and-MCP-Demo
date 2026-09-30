"""The one Claude client every agent here shares, routed through OpenRouter (https://openrouter.ai).
OpenRouter speaks the Anthropic Messages API, so the SDK and our tool schemas work unchanged.
Configure it in the .env file next to this one, or with real environment variables (which win):
OPENROUTER_API_KEY (required to make calls), OPENROUTER_MODEL and OPENROUTER_BASE_URL (optional)."""
import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))   # an explicit path: never searches parent folders for someone else's .env

# The key travels as a Bearer token. api_key="" stops a stray ANTHROPIC_API_KEY from being sent to OpenRouter
# as a direct-Anthropic credential.
client = anthropic.Anthropic(
    base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api"),
    auth_token=os.environ.get("OPENROUTER_API_KEY"),
    api_key="",
)
MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.6")
