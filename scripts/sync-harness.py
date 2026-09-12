#!/usr/bin/env python3
"""Generate the per-harness files the neutral core does not carry.

A harness is the program that runs the agent loop. Each one reads roles and
MCP servers in its own format, from its own directory. This script renders
those files from the one copy of each source, so nothing under a harness's
directory is ever edited by hand:

- One role file per `agents/*.md`, in the format the adapter's manifest names.
  The role's frontmatter `name` and `description` and its body carry over.
  A `skills:` line becomes a preamble that names each skill file to read
  first. Extra keys, a model or a sandbox mode, come from the adapter's
  mapping file, never from the role file.
- One block of MCP server tables, from the workbench's MCP source file, in the
  format the manifest names, appended to a hand-edited head.

Every path, every format identifier and every harness fact comes from
`adapters/<id>/wiring.json`. This script names no harness. A manifest holds:

    {"links":  {"<path>": "<target>", ...},
     "roles":  {"format": "<id>", "dir": "<path>", "mapping": "<file>"},
     "mcp":    {"format": "<id>", "source": "<file>", "path": "<path>",
                "head": "<file>"}}

`links` is read by check-harness.py and ignored here. `roles` and `mcp` are
each optional. `mapping` and `head` are relative to the adapter directory;
every other path is relative to the workbench root.

Usage:

    python3 scripts/sync-harness.py              write what is stale
    python3 scripts/sync-harness.py --check      report, write nothing
    python3 scripts/sync-harness.py --root PATH  another tree

Exit 0 when nothing is stale, or after writing. Exit 1 from `--check` when a
generated file is missing, differs from its source, or has no source left
(an orphan). Exit 2 on an input the script cannot use: an unreadable
manifest, a role with no frontmatter, a mapping naming a role that does not
exist, a format nobody registered, or an MCP server it cannot express in the
target format. Exit 2 names the file and the cause on stderr and writes
nothing.

Standard library only. It loads `check-roles.py` for its frontmatter parser,
so the two scripts read a role file the same way.
"""

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ADAPTERS_DIR = "adapters"
MANIFEST = "wiring.json"
GENERATED_MARK = "generated from {source} by scripts/sync-harness.py; do not edit below"


class SyncError(Exception):
    """An input the script cannot use. Exit 2, nothing written."""


def _load_check_roles():
    spec = importlib.util.spec_from_file_location("check_roles", HERE / "check-roles.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_roles = _load_check_roles()


# --- TOML rendering ----------------------------------------------------------

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _escape_control(text):
    return _CONTROL.sub(lambda m: "\\u%04X" % ord(m.group()), text)


def toml_basic(text):
    """One-line basic string, quoted."""
    out = text.replace("\\", "\\\\").replace('"', '\\"')
    out = out.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"' + _escape_control(out) + '"'


def toml_multiline(text):
    """Multi-line basic string. The newline after the opening delimiter is
    trimmed by TOML, so the body's first line is preserved. A run of three
    quotes inside the body would close the string, so every such run gets its
    third quote escaped. Carriage returns are escaped rather than kept, since
    a bare CR is not legal inside the string."""
    out = text.replace("\\", "\\\\")
    out = out.replace('"""', '""\\"')
    out = out.replace("\r", "\\r")
    out = _escape_control(out)
    # One or two unescaped quotes before the closing delimiter are legal
    # TOML; three cannot occur, because every run of three was escaped above.
    return '"""\n' + out + '"""'


def _toml_value(key, value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return toml_basic(value)
    raise SyncError(f"mapping key {key!r}: only strings and booleans are rendered, not {type(value).__name__}")


BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")
AGENT_KEYS = ("name", "description", "developer_instructions")


def _bare_key(key, where):
    """A key written unquoted in TOML. Anything else would be written as a
    dotted path or refused by the parser, and both are silent here."""
    if not isinstance(key, str) or not BARE_KEY.fullmatch(key):
        raise SyncError(f"{where}: key {key!r} is not a bare TOML key (letters, digits, _ and -)")
    return key


def render_toml_agent(source_rel, name, description, body, skills, extra):
    """One agent file: a header comment, name, description, the extra keys in
    the order the mapping gave them, and the body as developer_instructions."""
    lines = [
        f"# Generated by scripts/sync-harness.py from {source_rel}. Do not edit here.",
        f"name = {toml_basic(name)}",
        f"description = {toml_basic(description)}",
    ]
    for key, value in extra.items():
        _bare_key(key, f"mapping for {name}")
        if key in AGENT_KEYS:
            raise SyncError(f"mapping for {name}: key {key!r} is set from the role file, not the mapping")
        lines.append(f"{key} = {_toml_value(key, value)}")
    instructions = body
    if skills:
        files = ", ".join(f"`skills/{s}/SKILL.md`" for s in skills)
        instructions = f"Before you start, read each of these files in full: {files}.\n\n" + body
    lines.append(f"developer_instructions = {toml_multiline(instructions)}")
    return "\n".join(lines) + "\n"


def render_toml_mcp_servers(servers, source_rel):
    """`[mcp_servers.<name>]` tables from the `mcpServers` object of the source
    file. Two shapes map: a local command, and a remote URL with at most a
    bearer token read from an environment variable. Anything else is refused
    by name, because a table the harness reads differently from the source
    would be a server that works on one harness and silently not the other."""
    out = [f"# --- {GENERATED_MARK.format(source=source_rel)} ---"]
    for name in sorted(servers):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise SyncError(f"{source_rel}: server {name!r}: the name must be letters, digits, _ or -")
        spec = servers[name]
        if not isinstance(spec, dict):
            raise SyncError(f"{source_rel}: server {name!r}: is not an object")
        kind = spec.get("type", "stdio")
        keys = set(spec) - {"type"}
        where = f"{source_rel}: server {name!r}"
        out.append("")
        out.append(f"[mcp_servers.{name}]")
        if kind == "stdio":
            if not isinstance(spec.get("command"), str):
                raise SyncError(f"{where}: a local server needs a command, as a string")
            if not keys <= {"command", "args", "env"}:
                extra = ", ".join(sorted(keys - {"command", "args", "env"}))
                raise SyncError(f"{where}: key(s) not rendered: {extra}")
            _no_expansion(source_rel, name, spec)
            out.append(f"command = {toml_basic(spec['command'])}")
            args = spec.get("args", [])
            if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                raise SyncError(f"{where}: args must be a list of strings")
            out.append("args = [" + ", ".join(toml_basic(a) for a in args) + "]")
            env = spec.get("env", {})
            if env:
                if not isinstance(env, dict) or not all(isinstance(v, str) for v in env.values()):
                    raise SyncError(f"{where}: env must map names to strings")
                out.append("")
                out.append(f"[mcp_servers.{name}.env]")
                for k in sorted(env):
                    out.append(f"{_bare_key(k, where + ' env')} = {toml_basic(env[k])}")
        elif kind in ("http", "sse"):
            if not isinstance(spec.get("url"), str):
                raise SyncError(f"{where}: a remote server needs a url, as a string")
            if not keys <= {"url", "headers"}:
                extra = ", ".join(sorted(keys - {"url", "headers"}))
                raise SyncError(f"{where}: key(s) not rendered: {extra}")
            out.append(f"url = {toml_basic(spec['url'])}")
            headers = spec.get("headers", {})
            if headers:
                if not isinstance(headers, dict):
                    raise SyncError(f"{where}: headers must be an object")
                token = _bearer_env(headers)
                if token is None:
                    raise SyncError(
                        f"{source_rel}: server {name!r}: only a header of the form "
                        f'Authorization: "Bearer ${{NAME}}" is rendered, as bearer_token_env_var')
                out.append(f"bearer_token_env_var = {toml_basic(token)}")
        else:
            raise SyncError(f"{source_rel}: server {name!r}: type {kind!r} is not rendered")
    return "\n".join(out) + "\n"


def _no_expansion(source_rel, name, spec):
    for field in ("command", "args", "env"):
        value = spec.get(field)
        blob = json.dumps(value) if value is not None else ""
        if "${" in blob:
            raise SyncError(
                f"{source_rel}: server {name!r}: {field} uses ${{...}} expansion, "
                f"which the target format does not perform")


def _bearer_env(headers):
    if list(headers) != ["Authorization"]:
        return None
    match = re.fullmatch(r"Bearer \$\{([A-Za-z_][A-Za-z0-9_]*)\}", str(headers["Authorization"]))
    return match.group(1) if match else None


# --- sources -----------------------------------------------------------------

def _read_text(path, rel):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SyncError(f"{rel}: cannot be read, {type(exc).__name__}")
    except UnicodeDecodeError:
        raise SyncError(f"{rel}: is not UTF-8 text")


def _read_json(path, rel):
    try:
        return json.loads(_read_text(path, rel))
    except json.JSONDecodeError as exc:
        raise SyncError(f"{rel}: is not valid JSON, {exc}")


def _contained(root, rel_path, where):
    """A relative path that stays inside the root, normalised to posix."""
    if not isinstance(rel_path, str) or not rel_path.strip():
        raise SyncError(f"{where}: is not a path")
    if Path(rel_path).is_absolute():
        raise SyncError(f"{where}: {rel_path!r} is absolute; give a path relative to the workbench root")
    if ".." in Path(rel_path).parts:
        # No manifest path has a reason to climb. One that does is either a
        # mistake or a way to point the orphan sweep at files it never wrote.
        raise SyncError(f"{where}: {rel_path!r} contains '..'; give a plain path under the workbench root")
    normal = Path(os.path.normpath(rel_path)).as_posix()
    if normal == ".":
        raise SyncError(f"{where}: {rel_path!r} is the workbench root itself")
    return normal


def load_manifests(root):
    """Every adapters/<id>/wiring.json, as (id, manifest), sorted by id."""
    adapters = root / ADAPTERS_DIR
    if not adapters.is_dir():
        return []
    found = []
    for path in sorted(adapters.glob(f"*/{MANIFEST}")):
        rel = path.relative_to(root).as_posix()
        manifest = _read_json(path, rel)
        if not isinstance(manifest, dict):
            raise SyncError(f"{rel}: the top level is not an object")
        found.append((path.parent.name, manifest))
    return found


def role_sources(root):
    """name -> (fields, body, skills) for every agents/*.md except README.md."""
    agents = root / "agents"
    if not agents.is_dir():
        raise SyncError("agents/: directory not found")
    roles = {}
    for path in sorted(agents.glob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(root).as_posix()
        failures = []
        parsed = check_roles.parse(path, rel, failures)
        if parsed is None:
            raise SyncError(failures[0])
        fields, lists, continued = parsed
        skills = check_roles.named_skills(fields, lists, continued, rel, failures)
        if failures:
            raise SyncError(failures[0])
        name = fields.get("name", "").strip()
        if not check_roles.NAME_RE.match(name) or name != path.stem:
            raise SyncError(
                f"{rel}: name {name!r} must be lowercase letters, digits and single "
                f"hyphens, and must equal the filename {path.stem!r}")
        text = _read_text(path, rel)
        body = text[check_roles.FRONT_RE.match(text).end():]
        body = body.lstrip("\n").rstrip() + "\n"
        roles[name] = (rel, fields, body, skills)
    return roles


ROLE_FORMATS = {"toml-agent": render_toml_agent}
MCP_FORMATS = {"toml-mcp-servers": render_toml_mcp_servers}


def _role_outputs(root, adapter, block, outputs):
    for key in ("format", "dir", "mapping"):
        if key not in block:
            raise SyncError(f"adapters/{adapter}/{MANIFEST}: roles block has no {key!r}")
    render = ROLE_FORMATS.get(block["format"])
    if render is None:
        raise SyncError(f"adapters/{adapter}/{MANIFEST}: role format {block['format']!r} is not registered")
    where = f"adapters/{adapter}/{MANIFEST}: roles.dir"
    directory = _contained(root, block["dir"], where)
    mapping_rel = f"{ADAPTERS_DIR}/{adapter}/{block['mapping']}"
    mapping = _read_json(root / mapping_rel, mapping_rel)
    if not isinstance(mapping, dict):
        raise SyncError(f"{mapping_rel}: the top level is not an object")
    defaults = mapping.get("defaults", {})
    per_role = mapping.get("roles", {})
    if not isinstance(defaults, dict):
        raise SyncError(f"{mapping_rel}: defaults is not an object")
    if not isinstance(per_role, dict):
        raise SyncError(f"{mapping_rel}: roles is not an object")
    roles = role_sources(root)
    for name, entry in per_role.items():
        if name not in roles:
            raise SyncError(f"{mapping_rel}: role {name!r} has no agents/{name}.md")
        if not isinstance(entry, dict):
            raise SyncError(f"{mapping_rel}: role {name!r} is not an object")
    for name, (rel, fields, body, skills) in roles.items():
        extra = dict(defaults)
        extra.update(per_role.get(name, {}))
        out_rel = f"{directory}/{name}.toml"
        outputs[out_rel] = render(rel, name, fields.get("description", ""), body, skills, extra)


def _mcp_outputs(root, adapter, block, outputs):
    for key in ("format", "source", "path", "head"):
        if key not in block:
            raise SyncError(f"adapters/{adapter}/{MANIFEST}: mcp block has no {key!r}")
    render = MCP_FORMATS.get(block["format"])
    if render is None:
        raise SyncError(f"adapters/{adapter}/{MANIFEST}: mcp format {block['format']!r} is not registered")
    where = f"adapters/{adapter}/{MANIFEST}: mcp"
    source_rel = _contained(root, block["source"], where + ".source")
    out_rel = _contained(root, block["path"], where + ".path")
    source = _read_json(root / source_rel, source_rel)
    servers = source.get("mcpServers") if isinstance(source, dict) else None
    if not isinstance(servers, dict):
        raise SyncError(f"{source_rel}: no mcpServers object at the top level")
    head_rel = f"{ADAPTERS_DIR}/{adapter}/{block['head']}"
    head = _read_text(root / head_rel, head_rel)
    if head and not head.endswith("\n"):
        head += "\n"
    outputs[out_rel] = head + "\n" + render(servers, source_rel)


def expected_outputs(root):
    """Every generated file the manifests imply: relative posix path -> text."""
    root = Path(root)
    outputs = {}
    for adapter, manifest in load_manifests(root):
        if "roles" in manifest:
            _role_outputs(root, adapter, manifest["roles"], outputs)
        if "mcp" in manifest:
            _mcp_outputs(root, adapter, manifest["mcp"], outputs)
    return outputs


def _orphans(root, outputs):
    """Generated role files whose source role is gone."""
    found = []
    for adapter, manifest in load_manifests(root):
        block = manifest.get("roles")
        if not isinstance(block, dict) or "dir" not in block:
            continue
        directory = root / _contained(root, block["dir"], f"adapters/{adapter}/{MANIFEST}: roles.dir")
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.toml")):
            rel = path.relative_to(root).as_posix()
            if rel not in outputs:
                found.append(rel)
    return found


def stale(root):
    """One line per file that is missing, differs, or has no source."""
    root = Path(root)
    outputs = expected_outputs(root)
    lines = []
    for rel, text in sorted(outputs.items()):
        path = root / rel
        if not path.is_file():
            lines.append(f"missing: {rel}")
        elif _read_text(path, rel) != text:
            lines.append(f"stale: {rel}")
    lines.extend(f"orphan: {rel}" for rel in _orphans(root, outputs))
    return lines


def write(root):
    """Write every stale or missing file, delete every orphan."""
    root = Path(root)
    outputs = expected_outputs(root)
    lines = []
    for rel, text in sorted(outputs.items()):
        path = root / rel
        if path.is_file() and _read_text(path, rel) == text:
            lines.append(f"unchanged: {rel}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        lines.append(f"wrote: {rel}")
    for rel in _orphans(root, outputs):
        (root / rel).unlink()
        lines.append(f"deleted: {rel}")
    return lines


def main(argv):
    args = list(argv[1:])
    root = HERE.parent
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            print("--root needs a path", file=sys.stderr)
            return 2
        root = Path(args[i + 1])
        del args[i:i + 2]
    check = "--check" in args
    if check:
        args.remove("--check")
    if args:
        print(f"unknown argument(s): {' '.join(args)}", file=sys.stderr)
        return 2
    try:
        lines = stale(root) if check else write(root)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    if check:
        print(f"{len(lines)} stale file(s)")
        return 1 if lines else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
