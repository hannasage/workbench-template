"""Tests for scripts/sync-harness.py.

The script renders, per adapter manifest, the generated files a harness
needs that the neutral core does not carry: one role file per agents/*.md in
the harness's own format, and one block of MCP server tables from the
workbench's MCP source. Every path and format identifier comes from
adapters/*/wiring.json; the script names no harness.

Standard library only. Run with:

    python3 -m unittest discover -s scripts/tests
"""

import ast
import importlib.util
import json
import os
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "sync-harness.py"
WORKBENCH_ROOT = SCRIPT_PATH.parent.parent

_spec = importlib.util.spec_from_file_location("sync_harness", SCRIPT_PATH)
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)


def role_md(name, description="Does one thing.", body="Body line one.\n", skills=None):
    front = f"---\nname: {name}\ndescription: {description}\n"
    if skills:
        front += f"skills: {skills}\n"
    return front + "---\n\n" + body


ROLES_MANIFEST = {
    "links": {},
    "roles": {"format": "toml-agent", "dir": ".x/agents", "mapping": "roles.json"},
}


class Fixture:
    """A workbench tree under a temporary directory."""

    def __init__(self, manifest=None, mapping=None):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.write("agents/README.md", "# not a role\n")
        self.write("agents/alpha.md", role_md("alpha"))
        self.write("skills/one/SKILL.md", "---\nname: one\ndescription: d\n---\n")
        self.write("adapters/x/wiring.json", json.dumps(manifest or ROLES_MANIFEST))
        self.write("adapters/x/roles.json", json.dumps(mapping or {"defaults": {}, "roles": {}}))

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def cleanup(self):
        self._tmp.cleanup()


class SyncHarnessTest(unittest.TestCase):

    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)
        self.root = self.fx.root

    # -- TOML string rendering ------------------------------------------------

    def test_basic_string_escapes_backslash_quote_newline_and_control(self):
        self.assertEqual(sync.toml_basic('a\\b"c\nd\te\x01'), '"a\\\\b\\"c\\nd\\te\\u0001"')

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_multiline_string_round_trips_awkward_bodies(self):
        bodies = [
            'plain\n',
            'has """ three quotes\n',
            'has """" four quotes\n',
            'ends with a quote "\n',
            'ends with two quotes ""\n',
            'back\\slash and \\" escaped-looking text\n',
            'control \x01 char and tab\t\n',
            'windows\r\nline\n',
            'trailing """',
        ]
        for body in bodies:
            with self.subTest(body=body):
                doc = "v = " + sync.toml_multiline(body) + "\n"
                self.assertEqual(tomllib.loads(doc)["v"], body)

    # -- rendering one role -----------------------------------------------------

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_renders_name_description_and_body_as_developer_instructions(self):
        text = sync.render_toml_agent(
            "agents/alpha.md", "alpha", 'Does "one" thing.', "Body\nmore\n", [], {})
        doc = tomllib.loads(text)
        self.assertEqual(doc["name"], "alpha")
        self.assertEqual(doc["description"], 'Does "one" thing.')
        self.assertEqual(doc["developer_instructions"], "Body\nmore\n")
        self.assertIn("agents/alpha.md", text.splitlines()[0])
        self.assertTrue(text.splitlines()[0].startswith("#"))

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_skills_preamble_names_each_skill_file_before_the_body(self):
        text = sync.render_toml_agent(
            "agents/alpha.md", "alpha", "d", "Body\n", ["one", "two"], {})
        instructions = tomllib.loads(text)["developer_instructions"]
        preamble, _, rest = instructions.partition("\n\n")
        self.assertIn("skills/one/SKILL.md", preamble)
        self.assertIn("skills/two/SKILL.md", preamble)
        self.assertEqual(rest, "Body\n")

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_no_skills_means_no_preamble(self):
        text = sync.render_toml_agent("agents/alpha.md", "alpha", "d", "Body\n", [], {})
        self.assertEqual(tomllib.loads(text)["developer_instructions"], "Body\n")

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_extra_keys_from_the_mapping_are_emitted_as_top_level_values(self):
        text = sync.render_toml_agent(
            "agents/alpha.md", "alpha", "d", "Body\n", [],
            {"model": "m-1", "sandbox_mode": "read-only", "flag": True})
        doc = tomllib.loads(text)
        self.assertEqual(doc["model"], "m-1")
        self.assertEqual(doc["sandbox_mode"], "read-only")
        self.assertIs(doc["flag"], True)

    def test_extra_key_of_an_unsupported_type_is_an_input_error(self):
        with self.assertRaises(sync.SyncError):
            sync.render_toml_agent("agents/alpha.md", "alpha", "d", "B\n", [], {"n": 3.5})

    # -- expected outputs from the manifests ----------------------------------

    def test_one_output_per_role_and_readme_is_not_a_role(self):
        self.fx.write("agents/beta.md", role_md("beta"))
        outputs = sync.expected_outputs(self.root)
        self.assertEqual(sorted(outputs), [".x/agents/alpha.toml", ".x/agents/beta.toml"])

    def test_manifest_without_roles_block_produces_no_role_files(self):
        self.fx.write("adapters/x/wiring.json", json.dumps({"links": {"L": "T"}}))
        self.assertEqual(sync.expected_outputs(self.root), {})

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_mapping_role_entry_overrides_defaults(self):
        self.fx.write("adapters/x/roles.json", json.dumps(
            {"defaults": {"model": "m-default", "sandbox_mode": "read-only"},
             "roles": {"alpha": {"model": "m-alpha"}}}))
        doc = tomllib.loads(sync.expected_outputs(self.root)[".x/agents/alpha.toml"])
        self.assertEqual(doc["model"], "m-alpha")
        self.assertEqual(doc["sandbox_mode"], "read-only")

    def test_mapping_that_names_a_role_with_no_source_file_is_an_input_error(self):
        self.fx.write("adapters/x/roles.json", json.dumps(
            {"defaults": {}, "roles": {"ghost": {"model": "m"}}}))
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        self.assertIn("ghost", str(ctx.exception))

    def test_unknown_format_identifier_is_an_input_error(self):
        manifest = {"roles": {"format": "yaml-thing", "dir": ".x/agents", "mapping": "roles.json"}}
        self.fx.write("adapters/x/wiring.json", json.dumps(manifest))
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        self.assertIn("yaml-thing", str(ctx.exception))

    def test_unreadable_manifest_json_is_an_input_error_naming_the_file(self):
        self.fx.write("adapters/x/wiring.json", "{not json")
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        self.assertIn("adapters/x/wiring.json", str(ctx.exception))

    def test_malformed_role_frontmatter_is_an_input_error(self):
        self.fx.write("agents/bad.md", "no frontmatter here\n")
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        self.assertIn("agents/bad.md", str(ctx.exception))

    # -- stale, write, orphans --------------------------------------------------

    def test_stale_reports_every_missing_file_before_the_first_write(self):
        self.assertEqual(sync.stale(self.root), ["missing: .x/agents/alpha.toml"])

    def test_write_then_stale_is_clean(self):
        lines = sync.write(self.root)
        self.assertEqual(lines, ["wrote: .x/agents/alpha.toml"])
        self.assertEqual(sync.stale(self.root), [])
        self.assertTrue((self.root / ".x/agents/alpha.toml").is_file())

    def test_edited_output_is_reported_stale(self):
        sync.write(self.root)
        path = self.root / ".x/agents/alpha.toml"
        path.write_text(path.read_text(encoding="utf-8") + "# hand edit\n", encoding="utf-8")
        self.assertEqual(sync.stale(self.root), ["stale: .x/agents/alpha.toml"])

    def test_orphan_is_reported_by_check_and_deleted_by_write(self):
        sync.write(self.root)
        self.fx.write(".x/agents/gone.toml", 'name = "gone"\n')
        self.assertEqual(sync.stale(self.root), ["orphan: .x/agents/gone.toml"])
        lines = sync.write(self.root)
        self.assertIn("deleted: .x/agents/gone.toml", lines)
        self.assertFalse((self.root / ".x/agents/gone.toml").exists())

    def test_write_reports_unchanged_files_as_unchanged(self):
        sync.write(self.root)
        self.assertEqual(sync.write(self.root), ["unchanged: .x/agents/alpha.toml"])

    # -- MCP servers ------------------------------------------------------------

    MCP_MANIFEST = {
        "links": {},
        "mcp": {"format": "toml-mcp-servers", "source": ".mcp.json",
                "path": ".x/config.toml", "head": "config.toml"},
    }

    def _mcp_tree(self, servers, head="# head line\n"):
        self.fx.write("adapters/x/wiring.json", json.dumps(self.MCP_MANIFEST))
        self.fx.write("adapters/x/config.toml", head)
        self.fx.write(".mcp.json", json.dumps({"mcpServers": servers}))

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_local_server_maps_command_args_and_env(self):
        self._mcp_tree({"local": {
            "command": "npx", "args": ["-y", "some-server"], "env": {"TOKEN_FILE": "/tmp/t"}}})
        text = sync.expected_outputs(self.root)[".x/config.toml"]
        doc = tomllib.loads(text)
        self.assertEqual(doc["mcp_servers"]["local"]["command"], "npx")
        self.assertEqual(doc["mcp_servers"]["local"]["args"], ["-y", "some-server"])
        self.assertEqual(doc["mcp_servers"]["local"]["env"], {"TOKEN_FILE": "/tmp/t"})

    @unittest.skipUnless(tomllib, "tomllib needs Python 3.11")
    def test_remote_server_maps_url_and_bearer_token_variable(self):
        self._mcp_tree({"remote": {
            "type": "http", "url": "https://example.test/mcp",
            "headers": {"Authorization": "Bearer ${REMOTE_TOKEN}"}}})
        doc = tomllib.loads(sync.expected_outputs(self.root)[".x/config.toml"])
        self.assertEqual(doc["mcp_servers"]["remote"]["url"], "https://example.test/mcp")
        self.assertEqual(doc["mcp_servers"]["remote"]["bearer_token_env_var"], "REMOTE_TOKEN")

    def test_head_comes_first_then_the_marker_then_the_tables(self):
        self._mcp_tree({"a": {"command": "c"}}, head="# my head\n")
        text = sync.expected_outputs(self.root)[".x/config.toml"]
        lines = text.splitlines()
        self.assertEqual(lines[0], "# my head")
        self.assertTrue(any("do not edit below" in l for l in lines))
        self.assertLess(lines.index(next(l for l in lines if "do not edit below" in l)),
                        lines.index("[mcp_servers.a]"))

    def test_empty_source_yields_head_and_marker_only(self):
        self._mcp_tree({})
        text = sync.expected_outputs(self.root)[".x/config.toml"]
        self.assertNotIn("[mcp_servers", text)
        self.assertIn("do not edit below", text)

    def test_missing_source_is_an_input_error_naming_it(self):
        self._mcp_tree({})
        (self.root / ".mcp.json").unlink()
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        self.assertIn(".mcp.json", str(ctx.exception))

    def _rejects(self, servers, *needles):
        self._mcp_tree(servers)
        with self.assertRaises(sync.SyncError) as ctx:
            sync.expected_outputs(self.root)
        for needle in needles:
            self.assertIn(needle, str(ctx.exception))

    def test_rejects_expansion_in_a_local_server(self):
        self._rejects({"s": {"command": "run", "env": {"K": "${HOME}/x"}}}, "'s'", "expansion")

    def test_rejects_a_header_that_is_not_a_bearer_variable(self):
        self._rejects({"s": {"type": "http", "url": "https://x", "headers": {"X-Key": "abc"}}},
                      "'s'", "bearer_token_env_var")

    def test_rejects_a_literal_bearer_token(self):
        self._rejects({"s": {"type": "http", "url": "https://x",
                             "headers": {"Authorization": "Bearer abc123"}}}, "'s'")

    def test_rejects_an_unknown_key(self):
        self._rejects({"s": {"command": "run", "timeout": 5}}, "'s'", "timeout")

    def test_rejects_a_server_name_that_is_not_a_bare_toml_key(self):
        self._rejects({"my server": {"command": "run"}}, "'my server'")

    def test_rejects_a_local_server_with_no_command(self):
        self._rejects({"s": {"args": ["x"]}}, "'s'", "command")

    def test_rejects_an_unknown_type(self):
        self._rejects({"s": {"type": "grpc", "url": "u"}}, "'s'", "grpc")

    # -- the command line -------------------------------------------------------

    def _cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True, text=True, cwd=self.root,
        )

    def test_check_exits_1_and_names_the_path_and_writes_nothing(self):
        result = self._cli("--check", "--root", str(self.root))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing: .x/agents/alpha.toml", result.stdout)
        self.assertFalse((self.root / ".x").exists())

    def test_default_run_writes_and_exits_0_then_check_exits_0(self):
        result = self._cli("--root", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("wrote: .x/agents/alpha.toml", result.stdout)
        result = self._cli("--check", "--root", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_input_error_exits_2_and_names_the_cause_on_stderr(self):
        self.fx.write("adapters/x/wiring.json", "{not json")
        result = self._cli("--check", "--root", str(self.root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("adapters/x/wiring.json", result.stderr)

    def test_missing_agents_directory_exits_2(self):
        for name in ("alpha.md", "README.md"):
            (self.root / "agents" / name).unlink()
        (self.root / "agents").rmdir()
        result = self._cli("--check", "--root", str(self.root))
        self.assertEqual(result.returncode, 2)
        self.assertIn("agents", result.stderr)

    def test_check_leaves_no_bytecode_cache_behind(self):
        """Other test files load the scripts through importlib and leave
        scripts/__pycache__ behind. Only the two files this script would
        write are cleared first and checked after."""
        cache = WORKBENCH_ROOT / "scripts" / "__pycache__"
        for stem in ("check-roles", "sync-harness"):
            for pyc in cache.glob(f"{stem}.*.pyc"):
                pyc.unlink()
        self._cli("--check", "--root", str(self.root))
        left = [p.name for stem in ("check-roles", "sync-harness") for p in cache.glob(f"{stem}.*.pyc")]
        self.assertEqual(left, [])
        self.assertEqual(list(self.root.rglob("__pycache__")), [])

    # -- housekeeping -----------------------------------------------------------

    def test_script_imports_nothing_outside_the_standard_library(self):
        stdlib_dir = Path(sysconfig.get_paths()["stdlib"]).resolve()
        tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        self.assertTrue(names)
        for name in names:
            spec = importlib.util.find_spec(name)
            self.assertIsNotNone(spec, f"{name} is not importable")
            origin = spec.origin
            is_builtin = origin in (None, "built-in", "frozen")
            is_stdlib = bool(origin) and Path(origin).resolve().is_relative_to(stdlib_dir) \
                and "site-packages" not in origin
            self.assertTrue(is_builtin or is_stdlib, f"{name} is not standard library")

    def test_script_names_no_harness(self):
        """scripts/ is in the neutral core. Every harness path comes from data."""
        text = SCRIPT_PATH.read_text(encoding="utf-8").lower()
        for token in ("claude", "codex", ".agents/"):
            self.assertNotIn(token, text, f"{token!r} appears in the script")

    def test_the_shipped_tree_is_current(self):
        """The committed generated files match their sources byte for byte."""
        self.assertEqual(sync.stale(WORKBENCH_ROOT), [])


if __name__ == "__main__":
    unittest.main()
