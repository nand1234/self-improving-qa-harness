"""Shared helpers for the harness-lab scripts."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARNESS_PARTS = ["agents", "skills", "agent-memory"]   # what gets copied into .claude/

# Check these against `claude --help` for your Claude Code version.
CLAUDE = "claude"
AGENT_TOOLS = "Read,Write,Edit,Agent"
EDITOR_TOOLS = "Read,Write,Edit"


def require_claude():
    if not shutil.which(CLAUDE):
        sys.exit("The claude CLI was not found. Install Claude Code, or use --dry-run.")


def make_workspace(harness_dir, prefix):
    """Create an isolated folder OUTSIDE the repo with the harness installed as .claude/.

    Outside the repo matters: Claude Code reads files and CLAUDE.md from parent folders,
    and the answer keys must stay out of the agent's reach.
    """
    ws = Path(tempfile.mkdtemp(prefix=prefix))
    for part in HARNESS_PARTS:
        src = Path(harness_dir) / part
        if src.exists():
            shutil.copytree(src, ws / ".claude" / part)
    return ws


def copy_harness(src, dst):
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for part in HARNESS_PARTS:
        if (Path(src) / part).exists():
            shutil.copytree(Path(src) / part, dst / part, dirs_exist_ok=True)


def run_claude(prompt, cwd, tools, timeout):
    cmd = [CLAUDE, "-p", prompt, "--allowedTools", tools]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
