#!/usr/bin/env python3
"""Prove the wiring between the neutral core and every adapter.

A harness is the program that runs the agent loop. The neutral core is every
part of the workbench that names no harness. Each adapter under `adapters/`
declares, in its `wiring.json`, the symlinks its harness discovers the core
through and the files it needs generated. This script checks that the tree
matches every declaration:

1. Every declared symlink exists, is a symlink, points at the declared target,
   and the target exists. Two adapters may declare the same link with the
   same target; two targets for one path is a failure.
2. Every `skills/<dir>/SKILL.md` is a readable file through every link that
   resolves to `skills/`, and every `agents/*.md` through every link that
   resolves to `agents/`. A link that exists but leads to a partial copy, or
   to the wrong directory, fails here with the file named.
3. Every generated file is current, by `sync-harness.py --check`.
4. No line in the neutral core matches a pattern in
   `adapters/harness-names.txt`, after tokens of the form `adapters/<id>/...`
   are removed from the line. A path into an adapter is a pointer, which the
   core may hold; the name of a harness is not.
5. The entrypoint `AGENTS.md` fits under the smallest documented size cap
   among the harnesses in the support matrix.

It proves wiring, not behaviour. Whether a harness loads the entrypoint,
dispatches a role, or runs a wiki operation is a separate test that does not
exist yet.

Usage:

    python3 scripts/check-harness.py [ROOT]

Prints one line per failure and then `N failure(s)`. The exit code is N,
capped at 125, so it can run as a pre-commit hook with no wrapper. A clean
tree prints `0 failure(s)` and exits 0.

Standard library only. This file names no harness: every path, name and
pattern comes from `adapters/`.
"""

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
NAMES_FILE = "adapters/harness-names.txt"
ENTRYPOINT = "AGENTS.md"
# 32 KiB: the smallest project-instruction size cap documented among the
# harnesses in the support matrix in adapters/README.md, which cites it.
ENTRYPOINT_CAP = 32768
# The permitted paths of the neutral core, per adapters/README.md. Absent ones
# are skipped; SPEC.md is on the list and the template ships none.
CORE_PATHS = (
    "AGENTS.md", "central-context", "skills", "agents", "scripts", "prompts",
    "DECISIONS.md", "SPEC.md", "README.md", ".gitignore",
)
ADAPTER_TOKEN = re.compile(r"adapters/[a-z0-9-]+(?:/[^\s`)]*)?")
SYMLINK_HINT = "On Windows: git config core.symlinks true, then git checkout -- ."


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_harness", HERE / "sync-harness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync = _load_sync()


# --- 1. links ----------------------------------------------------------------

def declared_links(root, failures):
    """path -> target across every manifest, with disagreements reported."""
    links, owners = {}, {}
    for adapter, manifest in sync.load_manifests(root):
        for path, target in (manifest.get("links") or {}).items():
            if path in links and links[path] != target:
                failures.append(
                    f"{path}: adapters/{owners[path]} declares {links[path]}, "
                    f"adapters/{adapter} declares {target}")
                continue
            links[path] = target
            owners[path] = adapter
    return links


def check_links(root, links, failures):
    for rel, target in links.items():
        path = root / rel
        if not path.is_symlink():
            if path.is_dir():
                failures.append(f"{rel}: is a directory, not a symlink to {target}. {SYMLINK_HINT}")
            elif path.exists():
                failures.append(f"{rel}: is a file, not a symlink to {target}. {SYMLINK_HINT}")
            else:
                failures.append(f"{rel}: missing. Expected a symlink to {target}")
            continue
        found = os.readlink(path)
        if found != target:
            failures.append(f"{rel}: points at {found}, not {target}")
            continue
        if not path.exists():
            failures.append(f"{rel}: target {target} does not exist")


# --- 2. reachability ---------------------------------------------------------

def _declared_destination(root, rel, target):
    return Path(os.path.normpath((root / rel).parent / target))


def check_reachable(root, links, failures):
    skills_dir = Path(os.path.normpath(root / "skills"))
    agents_dir = Path(os.path.normpath(root / "agents"))
    for rel, target in links.items():
        destination = _declared_destination(root, rel, target)
        if destination == skills_dir and skills_dir.is_dir():
            for skill in sorted(skills_dir.iterdir()):
                if skill.name.startswith(".") or not skill.is_dir():
                    continue
                source = f"skills/{skill.name}/SKILL.md"
                if (skills_dir / skill.name / "SKILL.md").is_file() \
                        and not (root / rel / skill.name / "SKILL.md").is_file():
                    failures.append(f"{source}: not reachable through {rel}")
        elif destination == agents_dir and agents_dir.is_dir():
            for role in sorted(agents_dir.glob("*.md")):
                if not (root / rel / role.name).is_file():
                    failures.append(f"agents/{role.name}: not reachable through {rel}")


# --- 3. generated files ------------------------------------------------------

def check_generated(root, failures):
    try:
        failures.extend(sync.stale(root))
    except sync.SyncError as exc:
        failures.append(str(exc))


# --- 4. the neutral core -----------------------------------------------------

def load_patterns(root, failures):
    """The compiled pattern, or None. No adapters directory at all is the
    doctrine's delete test, and then there is nothing to scan for; an adapters
    directory with no names file is a defect."""
    path = root / NAMES_FILE
    if not (root / sync.ADAPTERS_DIR).is_dir():
        return None
    if not path.is_file():
        failures.append(f"{NAMES_FILE}: missing")
        return None
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]
    if not lines:
        failures.append(f"{NAMES_FILE}: holds no pattern")
        return None
    try:
        return re.compile("|".join(f"(?:{l})" for l in lines), re.IGNORECASE)
    except re.error as exc:
        failures.append(f"{NAMES_FILE}: is not a valid pattern, {exc}")
        return None


def core_files(root):
    for name in CORE_PATHS:
        path = root / name
        if path.is_file():
            yield path
        elif path.is_dir():
            for sub in sorted(path.rglob("*")):
                parts = sub.relative_to(root).parts
                if any(p.startswith(".") or p == "__pycache__" for p in parts):
                    continue
                if sub.is_file() and not sub.is_symlink():
                    yield sub


def check_neutral_core(root, failures):
    pattern = load_patterns(root, failures)
    if pattern is None:
        return
    for path in core_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            match = pattern.search(ADAPTER_TOKEN.sub("", line))
            if match:
                failures.append(f"{rel}:{lineno}: names a harness: {match.group()}")


# --- 5. the entrypoint cap ---------------------------------------------------

def check_entrypoint_size(root, failures):
    path = root / ENTRYPOINT
    if not path.is_file():
        failures.append(f"{ENTRYPOINT}: missing")
        return
    size = path.stat().st_size
    if size > ENTRYPOINT_CAP:
        failures.append(
            f"{ENTRYPOINT}: {size} bytes, over the {ENTRYPOINT_CAP}-byte cap "
            f"the smallest documented harness limit sets")


# --- run ---------------------------------------------------------------------

def run(root):
    """Every failure on one tree, in check order."""
    root = Path(root)
    failures = []
    links = declared_links(root, failures)
    check_links(root, links, failures)
    check_reachable(root, links, failures)
    check_generated(root, failures)
    check_neutral_core(root, failures)
    check_entrypoint_size(root, failures)
    return failures


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else HERE.parent
    failures = run(root)
    for line in failures:
        print(line)
    print(f"{len(failures)} failure(s)")
    return min(len(failures), 125)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
