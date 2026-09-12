"""Tests for scripts/check-harness.py.

The script proves the wiring between the neutral core and every adapter: the
symlinks each manifest declares exist and point where they say, every skill
and role is reachable through them, every generated file is current, no file
in the neutral core names a harness, and the entrypoint fits the smallest
documented size cap. It proves wiring, not behaviour.

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

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check-harness.py"
WORKBENCH_ROOT = SCRIPT_PATH.parent.parent

_spec = importlib.util.spec_from_file_location("check_harness", SCRIPT_PATH)
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def _can_symlink():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.symlink("a", os.path.join(tmp, "b"))
            return True
        except (OSError, NotImplementedError):
            return False


HAS_SYMLINKS = _can_symlink()

ROLE = "---\nname: alpha\ndescription: d\n---\n\nBody.\n"
SKILL = "---\nname: one\ndescription: d\n---\n"


class Fixture:
    """A tree with one role, one skill, one adapter, and correct wiring."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.write("AGENTS.md", "# entrypoint\n")
        self.write("README.md", "# readme\n")
        self.write("agents/README.md", "# roles\n")
        self.write("agents/alpha.md", ROLE)
        self.write("skills/one/SKILL.md", SKILL)
        self.write("adapters/harness-names.txt", "# names\nAcme Harness\n\\.acme\\b\n")
        self.write("adapters/x/wiring.json", json.dumps({
            "links": {"ENTRY.md": "AGENTS.md", ".acme/agents": "../agents", ".acme/skills": "../skills"},
            "roles": {"format": "toml-agent", "dir": ".acme/roles", "mapping": "roles.json"},
        }))
        self.write("adapters/x/roles.json", json.dumps({"defaults": {}, "roles": {}}))
        (self.root / ".acme").mkdir()
        os.symlink("AGENTS.md", self.root / "ENTRY.md")
        os.symlink("../agents", self.root / ".acme/agents")
        os.symlink("../skills", self.root / ".acme/skills")
        check.sync.write(self.root)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def cleanup(self):
        self._tmp.cleanup()


@unittest.skipUnless(HAS_SYMLINKS, "symlinks are not supported here")
class CheckHarnessTest(unittest.TestCase):

    def setUp(self):
        self.fx = Fixture()
        self.addCleanup(self.fx.cleanup)
        self.root = self.fx.root

    def test_a_correct_fixture_has_no_failures(self):
        self.assertEqual(check.run(self.root), [])

    # -- links ------------------------------------------------------------------

    def test_missing_link_is_named(self):
        (self.root / "ENTRY.md").unlink()
        self.assertEqual(check.run(self.root), ["ENTRY.md: missing. Expected a symlink to AGENTS.md"])

    def test_plain_file_where_a_link_should_be_gets_the_symlink_hint(self):
        (self.root / "ENTRY.md").unlink()
        self.fx.write("ENTRY.md", "AGENTS.md")
        failures = check.run(self.root)
        self.assertEqual(len(failures), 1)
        self.assertIn("ENTRY.md: is a file, not a symlink", failures[0])
        self.assertIn("core.symlinks", failures[0])

    def test_link_with_the_wrong_target_is_named_with_both_targets(self):
        (self.root / "ENTRY.md").unlink()
        os.symlink("README.md", self.root / "ENTRY.md")
        self.assertEqual(check.run(self.root),
                         ["ENTRY.md: points at README.md, not AGENTS.md"])

    def test_link_whose_target_does_not_exist_is_named(self):
        (self.root / "AGENTS.md").unlink()
        failures = check.run(self.root)
        self.assertIn("ENTRY.md: target AGENTS.md does not exist", failures)

    def test_two_manifests_may_declare_the_same_link_with_the_same_target(self):
        self.fx.write("adapters/y/wiring.json", json.dumps({"links": {"ENTRY.md": "AGENTS.md"}}))
        self.assertEqual(check.run(self.root), [])

    def test_two_manifests_disagreeing_on_a_target_is_a_failure(self):
        self.fx.write("adapters/y/wiring.json", json.dumps({"links": {"ENTRY.md": "README.md"}}))
        failures = check.run(self.root)
        self.assertTrue(any("ENTRY.md" in f and "adapters/x" in f and "adapters/y" in f for f in failures),
                        failures)

    # -- reachability -----------------------------------------------------------

    def test_a_skill_unreachable_through_a_skills_link_is_named(self):
        (self.root / ".acme/skills").unlink()
        (self.root / ".acme/skills").mkdir()
        failures = check.run(self.root)
        self.assertIn(".acme/skills: is a directory, not a symlink to ../skills", failures[0])
        self.assertTrue(any("skills/one/SKILL.md" in f and ".acme/skills" in f for f in failures), failures)

    def test_a_role_unreachable_through_an_agents_link_is_named(self):
        (self.root / ".acme/agents").unlink()
        os.symlink("../skills", self.root / ".acme/agents")
        failures = check.run(self.root)
        self.assertTrue(any("agents/alpha.md" in f and ".acme/agents" in f for f in failures), failures)

    # -- generated files --------------------------------------------------------

    def test_a_stale_generated_file_is_a_failure(self):
        path = self.root / ".acme/roles/alpha.toml"
        path.write_text(path.read_text(encoding="utf-8") + "# edit\n", encoding="utf-8")
        self.assertIn("stale: .acme/roles/alpha.toml", check.run(self.root))

    def test_a_generator_input_error_is_a_failure_not_a_crash(self):
        self.fx.write("adapters/x/roles.json", "{bad")
        failures = check.run(self.root)
        self.assertTrue(any("adapters/x/roles.json" in f for f in failures), failures)

    # -- the neutral core -------------------------------------------------------

    def test_a_harness_name_in_the_core_is_named_with_its_line(self):
        self.fx.write("AGENTS.md", "# entrypoint\n\nOpen Acme Harness here.\n")
        self.assertIn("AGENTS.md:3: names a harness: Acme Harness", check.run(self.root))

    def test_a_harness_directory_in_the_core_is_named(self):
        self.fx.write("skills/one/SKILL.md", SKILL + "\nRead .acme/config first.\n")
        failures = check.run(self.root)
        self.assertTrue(any("skills/one/SKILL.md:6" in f for f in failures), failures)

    def test_an_adapter_path_token_is_not_a_harness_name(self):
        self.fx.write("README.md", "# readme\n\nSee adapters/acme/README.md and adapters/acme/.\n")
        self.fx.write("adapters/harness-names.txt", "\\bacme\\b\n")
        self.assertEqual(check.run(self.root), [])

    def test_the_scan_skips_the_adapters_directory_and_dot_directories(self):
        self.fx.write("adapters/x/README.md", "Acme Harness everywhere.\n")
        self.fx.write(".acme/notes.md", "Acme Harness.\n")
        self.assertEqual(check.run(self.root), [])

    def test_a_missing_names_file_is_a_failure(self):
        (self.root / "adapters/harness-names.txt").unlink()
        self.assertIn("adapters/harness-names.txt: missing", check.run(self.root))

    def test_a_tree_with_no_adapters_directory_at_all_passes(self):
        """The doctrine's delete test: the neutral core passes its own checks
        with adapters/ gone. No manifest declares nothing, and with no
        directory there is no pattern to scan for."""
        import shutil
        shutil.rmtree(self.root / "adapters")
        self.assertEqual(check.run(self.root), [])

    # -- the entrypoint size cap -----------------------------------------------

    def test_an_entrypoint_over_the_cap_is_named_with_both_sizes(self):
        self.fx.write("AGENTS.md", "x" * (check.ENTRYPOINT_CAP + 1) + "\n")
        failures = check.run(self.root)
        self.assertTrue(any(f.startswith("AGENTS.md: ") and str(check.ENTRYPOINT_CAP) in f for f in failures),
                        failures)

    # -- the command line -------------------------------------------------------

    def _cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT_PATH), *args],
                              capture_output=True, text=True, cwd=cwd or self.root)

    def test_clean_tree_prints_zero_failures_and_exits_0(self):
        result = self._cli(str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 failure(s)", result.stdout)

    def test_exit_code_is_the_failure_count(self):
        (self.root / "ENTRY.md").unlink()
        self.fx.write("AGENTS.md", "Acme Harness\n")
        result = self._cli(str(self.root))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("2 failure(s)", result.stdout)

    def test_no_argument_resolves_the_root_from_the_script_location(self):
        result = self._cli(cwd=tempfile.gettempdir())
        self.assertIn("failure(s)", result.stdout)

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
        """scripts/ is in the neutral core. The pattern comes from the names
        file, so this test never has to name a harness either."""
        pattern = check.load_patterns(WORKBENCH_ROOT, [])
        self.assertIsNotNone(pattern)
        for lineno, line in enumerate(SCRIPT_PATH.read_text(encoding="utf-8").splitlines(), 1):
            self.assertIsNone(pattern.search(check.ADAPTER_TOKEN.sub("", line)),
                              f"line {lineno} names a harness")

    def test_the_shipped_tree_passes(self):
        self.assertEqual(check.run(WORKBENCH_ROOT), [])


if __name__ == "__main__":
    unittest.main()
