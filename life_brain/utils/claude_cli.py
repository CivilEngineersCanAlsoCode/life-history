"""
Claude CLI wrapper — replaces direct Anthropic API calls.
Uses `claude --print` subprocess (Claude Max subscription, zero API cost).

Per AGENTS.md rule: NEVER use Anthropic API keys or download separate models.
Always use `claude --print` — covered by Claude Max plan.

Usage (drop-in replacement for Anthropic client):
    from life_brain.utils.claude_cli import call_claude
    response = call_claude("Your prompt here")
    # Returns: str (response text)
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default model — fast for extraction tasks
DEFAULT_MODEL = "claude-sonnet-4-5"


def call_claude(
    prompt: str,
    system: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_retries: int = 2
) -> str:
    """
    Call Claude via CLI subprocess. Replaces Anthropic() client.

    Args:
        prompt: User message / prompt
        system: Optional system prompt
        model: Claude model (default: claude-sonnet-4-5)
        max_retries: Retry on timeout/error

    Returns:
        str: Claude's response text

    Raises:
        RuntimeError: If all retries fail
    """
    full_prompt = prompt
    if system:
        full_prompt = f"[System: {system}]\n\n{prompt}"

    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["claude", "--print", full_prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            logger.warning(f"Claude CLI attempt {attempt+1} failed: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Claude CLI timeout on attempt {attempt+1}")
        except FileNotFoundError:
            raise RuntimeError("claude CLI not found. Install: npm install -g @anthropic-ai/claude-cli")

    raise RuntimeError(f"Claude CLI failed after {max_retries+1} attempts")


class ClaudeCLIClient:
    """
    Drop-in replacement for anthropic.Anthropic() client.
    Implements the subset used in life_brain modules.

    Usage:
        # Before (Anthropic API):
        client = Anthropic()
        response = client.messages.create(model=..., messages=[{"role":"user","content":prompt}])
        text = response.content[0].text

        # After (Claude CLI):
        client = ClaudeCLIClient()
        text = client.complete(prompt)
    """

    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Complete a prompt — returns text directly."""
        return call_claude(prompt, system=system)

    class _Messages:
        def create(self, model: str, max_tokens: int, messages: list, **kwargs) -> "_Response":
            """Mimic anthropic.messages.create() interface."""
            # Extract user content from messages list
            user_content = ""
            system_content = kwargs.get("system", None)
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        # Handle content blocks
                        user_content = " ".join(
                            block.get("text", "") for block in content
                            if isinstance(block, dict) and block.get("type") == "text"
                        )
                    else:
                        user_content = str(content)
                    break

            text = call_claude(user_content, system=system_content)
            return ClaudeCLIClient._Response(text)

    class _Response:
        def __init__(self, text: str):
            self.content = [ClaudeCLIClient._ContentBlock(text)]

    class _ContentBlock:
        def __init__(self, text: str):
            self.text = text

    def __init__(self):
        self.messages = ClaudeCLIClient._Messages()


# Convenience alias — drop-in for `# Anthropic = ClaudeCLIClient  (defined at bottom of this file)`
Anthropic = ClaudeCLIClient
