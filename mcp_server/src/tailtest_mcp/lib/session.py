"""Session I/O -- load/save .cursor/hooks/state/tailtest.json and status helpers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Optional

from filter import _norm

_STATE_SUBPATH = os.path.join(".cursor", "hooks", "state", "tailtest.json")


def _state_path(project_root: str) -> str:
    return os.path.join(project_root, _STATE_SUBPATH)


def load_session(project_root: str) -> dict:
    """Load .cursor/hooks/state/tailtest.json.  Returns minimal empty dict if absent."""
    path = _state_path(project_root)
    if os.path.exists(path):
        try:
            with open(path) as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "pending_files": [],
        "touched_files": [],
        "runners": {},
        "fix_attempts": {},
        "deferred_failures": [],
        "generated_tests": {},
        "packages": {},
        "last_failures": [],
        "scenario_log": [],
        "complexity_scores": {},
    }


def save_session(project_root: str, session: dict) -> None:
    """Write session dict to .cursor/hooks/state/tailtest.json."""
    path = _state_path(project_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(session, fh, indent=2)
        fh.write("\n")


def is_git_tracked(file_path: str, project_root: str) -> Optional[bool]:
    """Return True if tracked by git, False if untracked, None if git unavailable."""
    if not os.path.isdir(os.path.join(project_root, ".git")):
        return None
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", os.path.abspath(file_path)],
            capture_output=True,
            cwd=project_root,
            timeout=2,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def determine_status(
    file_path: str,
    project_root: str,
    touched_files: list[str],
) -> str:
    """Return 'new-file' or 'legacy-file'.

    Git project:  tracked in git -> legacy-file,  untracked -> new-file.
    No-git:       first touch this session -> new-file,  repeat -> legacy-file.
    """
    rel_path = _norm(os.path.relpath(os.path.abspath(file_path), project_root))
    tracked = is_git_tracked(file_path, project_root)
    if tracked is None:
        return "legacy-file" if rel_path in touched_files else "new-file"
    return "legacy-file" if tracked else "new-file"


def find_package_root(
    rel_path: str,
    packages: dict,
) -> Optional[str]:
    """Return the relative path of the deepest package containing rel_path."""
    rel_path = _norm(rel_path)
    best: Optional[str] = None
    best_len = -1
    for pkg_rel in packages:
        pkg_prefix = _norm(pkg_rel).rstrip("/") + "/"
        if rel_path.startswith(pkg_prefix):
            if len(pkg_prefix) > best_len:
                best_len = len(pkg_prefix)
                best = pkg_rel
    return best
