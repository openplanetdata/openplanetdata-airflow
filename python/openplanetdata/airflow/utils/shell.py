"""Shell utilities for running commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(
    cmd: list[str],
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    log_file: str | Path | None = None,
) -> int:
    """
    Run a command and stream output to stdout/stderr or a log file.

    Args:
        cmd: Command and arguments as a list.
        cwd: Working directory for the command.
        env: Environment variables (merged with current env if provided).
        log_file: Optional file path to write stdout/stderr to.

    Returns:
        Exit code of the command.
    """
    import os

    full_env = {**os.environ, **(env or {})}

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=full_env,
            )
    else:
        result = subprocess.run(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd=cwd,
            env=full_env,
        )

    return result.returncode
