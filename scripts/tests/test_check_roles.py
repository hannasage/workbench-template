"""Tests for scripts/check-roles.py.

The behaviour under test is described in the script's own module docstring
and in scripts/README.md. This template ships no SPEC.md; write one when a
change here needs acceptance criteria of its own.

Each test method names the criterion number it covers in its docstring.
Standard library only: unittest, tempfile, pathlib, ast, subprocess, sysconfig,
importlib. Run with:

    python3 -m unittest discover -s scripts/tests

check-roles.py is never edited by this file. A failing test is a finding
about the script, not a reason to change the assertion.

The fixture registry below is written by hand for these tests, not copied
from scripts/model-registry.txt, so a test here never breaks just because
someone registers a new model on the real tree.
"""

import ast
import contextlib
import importlib.util
import io
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check-roles.py"
WORKBENCH_ROOT = SCRIPT_PATH.parent.parent

_spec = importlib.util.spec_from_file_location("check_roles", SCRIPT_PATH)
check_roles = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_roles)

# A minimal registry of the two shapes a model value takes: a short alias, and
# a full identifier with its dated spelling. Every value here is invented, so no
# test depends on one vendor's product names, and the real registry ships with
# no values at all.
FIXTURE_REGISTRY = """
alpha
alpha-model-9
alpha-model-9-20260101
""".strip() + "\n"


def skill_md(name, description="does a thing"):
    lines = ["---", f"name: {name}"]
    if description is not None:
        lines.append(f"description: {description}")
    lines.append("---")
    lines.append("Body.")
    return "\n".join(lines) + "\n"


def role_md(name, description="does a thing", model=None, skills=None, frontmatter=True):
    if not frontmatter:
        return "No frontmatter here.\n"
    lines = ["---", f"name: {name}"]
    if description is not None:
        lines.append(f"description: {description}")
    if model is not None:
        lines.append(f"model: {model}")
    if skills is not None:
        lines.append(f"skills: {skills}")
    lines.append("---")
    lines.append("Body.")
    return "\n".join(lines) + "\n"


class CheckRolesTest(unittest.TestCase):
    def _root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def _write(self, root, rel, text):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def _exempt(self, name="an-installed-skill"):
        """Mark one directory exempt for this test, restoring the real set after.

        THIRD_PARTY_SKILLS is empty in a fresh workbench and populated in one
        that has installed third-party skills. A test that indexes into the
        live set therefore errors in the first tree and passes in the second,
        which makes the suite depend on which clone it runs in. Supplying the
        exemption keeps the behaviour under test the same everywhere."""
        original = set(check_roles.THIRD_PARTY_SKILLS)
        check_roles.THIRD_PARTY_SKILLS.add(name)

        def restore():
            check_roles.THIRD_PARTY_SKILLS.clear()
            check_roles.THIRD_PARTY_SKILLS.update(original)

        self.addCleanup(restore)
        return name

    def _quiet_main(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = check_roles.main(argv)
        return code, buf.getvalue()

    def _base(self, registry=FIXTURE_REGISTRY):
        """A root with empty agents/, skills/, and a fixture model registry."""
        root = self._root()
        (root / "agents").mkdir()
        (root / "skills").mkdir()
        if registry is not None:
            self._write(root, "scripts/model-registry.txt", registry)
        return root

    # -- 1: a nested SKILL.md is a failure, named, at any depth --------------

    def test_nested_skill_file_one_level_deep_is_a_failure(self):
        """Criterion 1: skills/<dir>/nested/SKILL.md is reported, path named."""
        root = self._base()
        self._write(root, "skills/alpha/SKILL.md", skill_md("alpha"))
        self._write(root, "skills/alpha/nested/SKILL.md", skill_md("alpha"))
        failures, _ = check_roles.run(root)
        matches = [f for f in failures if f.startswith("skills/alpha/nested/SKILL.md")]
        self.assertEqual(len(matches), 1)
        self.assertIn("not discovered", matches[0])

    def test_nested_skill_file_several_levels_deep_is_also_a_failure(self):
        """Criterion 1: depth does not matter, skills/alpha/a/b/SKILL.md fails too."""
        root = self._base()
        self._write(root, "skills/alpha/SKILL.md", skill_md("alpha"))
        self._write(root, "skills/alpha/nested/SKILL.md", skill_md("alpha"))
        self._write(root, "skills/alpha/a/b/SKILL.md", skill_md("alpha"))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(f.startswith("skills/alpha/nested/SKILL.md") for f in failures))
        self.assertTrue(any(f.startswith("skills/alpha/a/b/SKILL.md") for f in failures))

    # -- 2: exactly one failure for a nested file, its frontmatter unread -----

    def test_nested_skill_with_broken_frontmatter_produces_only_the_nesting_failure(self):
        """Criterion 2: a nested file's frontmatter is never read, whatever it says."""
        root = self._base()
        self._write(root, "skills/alpha/SKILL.md", skill_md("alpha"))
        self._write(root, "skills/alpha/nested/SKILL.md", "not frontmatter at all, no ---\n")
        failures, _ = check_roles.run(root)
        related = [f for f in failures if "alpha/nested/SKILL.md" in f]
        self.assertEqual(len(related), 1)
        self.assertIn("not discovered", related[0])

    def test_valid_skill_next_to_a_nested_one_still_gets_checked(self):
        """Criterion 2 and 5: the directory's own SKILL.md is still checked
        when a nested one also exists; the nested failure does not replace it."""
        root = self._base()
        # Missing description on purpose, to prove the top-level file is
        # actually read and not skipped just because a nested file exists.
        self._write(root, "skills/gamma/SKILL.md", skill_md("gamma", description=None))
        self._write(root, "skills/gamma/nested/SKILL.md", skill_md("gamma"))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(f.startswith("skills/gamma/nested/SKILL.md") for f in failures))
        self.assertTrue(any(
            f.startswith("skills/gamma/SKILL.md") and "no description" in f
            for f in failures
        ))
        self.assertFalse(any("no SKILL.md" in f and "gamma" in f for f in failures))

    def test_directory_with_only_a_nested_skill_file_fails_once_not_twice(self):
        """Criterion 5: no own SKILL.md plus a nested one is the nesting
        failure only, never also a 'no SKILL.md' failure."""
        root = self._base()
        self._write(root, "skills/delta/deep/SKILL.md", skill_md("delta"))
        failures, _ = check_roles.run(root)
        delta_failures = [f for f in failures if "delta" in f]
        self.assertEqual(len(delta_failures), 1)
        self.assertIn("not discovered", delta_failures[0])

    # -- 3 and 4: a skill directory with nothing in it, dot dirs exempt -------

    def test_empty_skill_directory_is_one_failure_naming_it(self):
        """Criterion 3: a directory with no skill file of its own fails."""
        root = self._base()
        (root / "skills" / "epsilon").mkdir()
        failures, _ = check_roles.run(root)
        matches = [f for f in failures if f.startswith("skills/epsilon")]
        self.assertEqual(len(matches), 1)
        self.assertIn("no SKILL.md", matches[0])

    def test_dot_directory_under_skills_is_never_reported(self):
        """Criterion 4: skills/.obsidian/ holds no skill file and stays silent."""
        root = self._base()
        (root / "skills" / ".obsidian").mkdir()
        (root / "skills" / ".obsidian" / "graph.json").write_text("{}")
        failures, _ = check_roles.run(root)
        self.assertFalse(any(".obsidian" in f for f in failures))

    # -- 6, 7, 8, 9, 10: the name check and its one exemption ------------------

    def test_skill_name_mismatched_with_its_directory_fails(self):
        """Criterion 6: no allowlist protects a mismatched name by default."""
        root = self._base()
        self._write(root, "skills/my-new-skill/SKILL.md", skill_md("typoed-nmae"))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(
            f.startswith("skills/my-new-skill/SKILL.md") and "does not match directory" in f
            for f in failures
        ))

    def test_name_check_applies_to_every_skill_not_in_third_party_skills(self):
        """Criterion 7, rewritten from a source-shape check. The old version
        asserted the one module-level set literal was named THIRD_PARTY_SKILLS,
        which a real limiter written as a frozenset, tuple, or list would
        dodge. This tests the behaviour instead: every directory outside
        THIRD_PARTY_SKILLS gets the name check, whatever it is named."""
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("FIRST_PARTY_SKILLS", source)
        exempt = set(check_roles.THIRD_PARTY_SKILLS)
        candidates = ["my-new-skill", "wiki-query", "another-skill", "research-operations"]
        root = self._base()
        for name in candidates:
            self.assertNotIn(name, exempt, "fixture name collides with a real exemption")
            self._write(root, f"skills/{name}/SKILL.md", skill_md("mismatched-name"))
        failures, _ = check_roles.run(root)
        mismatched = {f.split("/")[1] for f in failures if "does not match directory" in f}
        self.assertEqual(mismatched, set(candidates))

    def test_directory_in_third_party_skills_is_exempt_from_the_name_check(self):
        """Criterion 8: the same mismatch that fails for an ordinary
        directory passes once the directory is one of the exempt ones."""
        exempt = self._exempt()
        root = self._base()
        self._write(root, f"skills/{exempt}/SKILL.md", skill_md("some-other-name"))
        failures, _ = check_roles.run(root)
        self.assertFalse(any(
            f.startswith(f"skills/{exempt}/SKILL.md") and "does not match directory" in f
            for f in failures
        ))

    def test_exempt_skill_with_no_description_still_fails(self):
        """Criterion 9: the exemption suppresses only the name-match check."""
        exempt = self._exempt()
        root = self._base()
        self._write(root, f"skills/{exempt}/SKILL.md", skill_md("some-other-name", description=None))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(
            f.startswith(f"skills/{exempt}/SKILL.md") and "no description" in f
            for f in failures
        ))
        self.assertFalse(any("does not match directory" in f for f in failures))

    def test_exempt_skill_with_uppercase_name_still_fails_the_shape_check(self):
        """Criterion 9 and 10: exemption does not touch the lowercase-hyphen
        shape check, even on an exempt directory."""
        exempt = self._exempt()
        root = self._base()
        self._write(root, f"skills/{exempt}/SKILL.md", skill_md("Some-Other-Name"))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(
            f.startswith(f"skills/{exempt}/SKILL.md") and "not lowercase-hyphen" in f
            for f in failures
        ))

    def test_ordinary_skill_with_uppercase_name_fails_the_shape_check(self):
        """Criterion 10: a name with a capital letter fails outside the
        exemption too, using the fixture 'lowercase-Name' example."""
        root = self._base()
        self._write(root, "skills/zeta/SKILL.md", skill_md("lowercase-Name"))
        failures, _ = check_roles.run(root)
        self.assertTrue(any(
            f.startswith("skills/zeta/SKILL.md") and "not lowercase-hyphen" in f
            for f in failures
        ))

    # -- 11 and 12: the registry-driven model check ----------------------------

    def test_registered_model_produces_nothing(self):
        """Criterion 11: an alias in the registry is not reported at all."""
        root = self._base()
        self._write(root, "agents/builder.md", role_md("builder", model="alpha"))
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    def test_registered_full_model_id_produces_nothing(self):
        """Criterion 11: a full model ID that is registered is not reported."""
        root = self._base()
        self._write(root, "agents/builder.md", role_md("builder", model="alpha-model-9"))
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    def test_unregistered_model_is_a_question_not_a_failure(self):
        """Criterion 11 (registry-driven design): an unregistered value is a
        question, never a failure."""
        root = self._base()
        self._write(root, "agents/builder.md", role_md("builder", model="alpha-model-8"))
        failures, questions = check_roles.run(root)
        self.assertFalse(any("alpha-model-8" in f for f in failures))
        self.assertTrue(any("alpha-model-8" in q for q in questions))

    def test_self_hosted_model_and_a_typo_are_treated_identically(self):
        """Criterion 11 (registry-driven design): alpha-model-8 (a plausible typo
        of a registered value) and local-model:32b (the tag form a self-hosted
        model takes) both land in questions, by the same rule, because the
        checker cannot tell them apart."""
        root = self._base()
        self._write(root, "agents/builder.md", role_md("builder", model="alpha-model-8"))
        self._write(root, "agents/critic.md", role_md("critic", model="local-model:32b"))
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        typo_q = [q for q in questions if "alpha-model-8" in q]
        local_q = [q for q in questions if "local-model:32b" in q]
        self.assertEqual(len(typo_q), 1)
        self.assertEqual(len(local_q), 1)
        # Same message shape for both: only the role file and the model
        # value differ, never the wording that explains the question.
        explanation = lambda q: q.split(": ", 1)[1]
        shape = lambda q, model: explanation(q).replace(model, "MODEL")
        self.assertEqual(shape(typo_q[0], "alpha-model-8"), shape(local_q[0], "local-model:32b"))

    def test_missing_registry_file_is_a_failure_and_stops_model_checking(self):
        """The registry-driven design: a missing registry file is a failure
        naming it, and no model value is checked against anything, so an
        otherwise-unregistered model produces no question either."""
        root = self._base(registry=None)
        self._write(root, "agents/builder.md", role_md("builder", model="alpha-model-8"))
        failures, questions = check_roles.run(root)
        self.assertTrue(any(
            f.startswith("scripts/model-registry.txt") and "missing" in f
            for f in failures
        ))
        self.assertEqual(questions, [])

    def test_real_model_registry_states_the_two_rules_a_reader_needs(self):
        """Criterion 12, adapted to the registry-driven design: the file that
        now holds the accepted model values (scripts/model-registry.txt, in
        place of an in-script constant) states both rules a reader acts on.
        A value is accepted only when it is listed, and an unlisted value is a
        question. The file names no harness and no vendor, so it cites no
        vendor's documentation and this test asks for none."""
        text = (WORKBENCH_ROOT / "scripts" / "model-registry.txt").read_text(encoding="utf-8")
        # The file is wrapped prose in comments, so a phrase may straddle two
        # lines. Flatten the comment markers and the whitespace before looking.
        flat = " ".join(text.replace("#", " ").split())
        self.assertIn("accepted only when it is listed", flat)
        self.assertIn("reported as a question", flat)
        self.assertIn("where you confirmed it", flat)

    # -- 13: agents/README.md is exempt from the frontmatter check -----------

    def test_agents_readme_with_no_frontmatter_produces_nothing(self):
        """Criterion 13: README.md is skipped even with no frontmatter."""
        root = self._base()
        self._write(root, "agents/README.md", "# Agents\n\nNo frontmatter here.\n")
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    # -- 14: the exit code formula, and the zero-failure message --------------

    def test_clean_tree_prints_zero_failures_and_exits_zero(self):
        """Criterion 14: a clean tree prints '0 failure(s)' and exits 0."""
        root = self._base()
        code, _ = self._quiet_main(["check-roles.py", str(root)])
        self.assertEqual(code, 0)

    def test_clean_tree_stdout_says_zero_failures(self):
        """Criterion 14: the exact '0 failure(s)' string on a clean tree."""
        root = self._base()
        _, out = self._quiet_main(["check-roles.py", str(root)])
        self.assertIn("0 failure(s)", out)
        self.assertNotIn("question(s)", out)

    def test_exit_code_is_failures_plus_questions(self):
        """Criterion 14: the exit code is the sum, not just the failure count."""
        root = self._base()
        (root / "skills" / "empty-one").mkdir()
        (root / "skills" / "empty-two").mkdir()
        self._write(root, "agents/builder.md", role_md("builder", model="alpha-model-8"))
        code, _ = self._quiet_main(["check-roles.py", str(root)])
        self.assertEqual(code, 3)

    def test_exit_code_caps_at_125_past_the_limit(self):
        """Criterion 14: the count caps at 125 even when failures exceed it."""
        root = self._base()
        for i in range(130):
            (root / "skills" / f"empty-{i}").mkdir()
        code, _ = self._quiet_main(["check-roles.py", str(root)])
        self.assertEqual(code, 125)

    # -- 15: every failure line starts with a path relative to the root -------

    def test_failure_lines_start_with_the_relative_path_across_several_failure_kinds(self):
        """Criterion 15: the offending path leads the line, not a prefix like
        the absolute temp directory or a generic label. Checked across five
        different failure kinds at once, not just the easiest one to trigger."""
        root = self._base()
        (root / "skills" / "epsilon").mkdir()                                    # no SKILL.md
        self._write(root, "skills/alpha/SKILL.md", skill_md("alpha"))
        self._write(root, "skills/alpha/nested/SKILL.md", skill_md("alpha"))     # nested
        self._write(root, "skills/zeta/SKILL.md", skill_md("mismatched"))        # skill name mismatch
        self._write(root, "agents/builder.md", role_md("wrong-name"))            # filename mismatch
        (root / "agents" / "binary.md").write_bytes(b"\x80\x81 not utf8")        # unreadable text
        failures, _ = check_roles.run(root)
        expected_prefixes = (
            "skills/epsilon",
            "skills/alpha/nested/SKILL.md",
            "skills/zeta/SKILL.md",
            "agents/builder.md",
            "agents/binary.md",
        )
        self.assertGreaterEqual(len(failures), len(expected_prefixes))
        for f in failures:
            self.assertTrue(f.startswith(expected_prefixes), f)
            self.assertNotIn(str(root), f)
        for prefix in expected_prefixes:
            self.assertTrue(any(f.startswith(prefix) for f in failures), prefix)

    # -- 16: default invocation checks the workbench root, cwd-independent ----

    def test_default_invocation_from_elsewhere_still_checks_container_root(self):
        """Criterion 16: no arguments, run with a different cwd, still checks
        the workbench root because it resolves from the script's own path."""
        elsewhere = self._root()
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=str(elsewhere),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("0 failure(s)", result.stdout)

    # -- 17: standard library only --------------------------------------------

    def test_script_imports_nothing_outside_the_standard_library(self):
        """Criterion 17: every top-level import resolves inside the stdlib."""
        # Both sides resolved: a Homebrew Python reports the stdlib through a
        # symlinked prefix while find_spec() returns the real Cellar path, and
        # is_relative_to() compares lexically.
        stdlib_dir = Path(sysconfig.get_paths()["stdlib"]).resolve()
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        self.assertTrue(names)
        for name in names:
            spec = importlib.util.find_spec(name)
            self.assertIsNotNone(spec, f"{name} is not importable at all")
            origin = spec.origin
            is_builtin = origin in (None, "built-in", "frozen")
            is_stdlib = bool(origin) \
                and Path(origin).resolve().is_relative_to(stdlib_dir) \
                and "site-packages" not in origin
            self.assertTrue(is_builtin or is_stdlib, f"{name} is not standard library")

    # -- 18: run(root) is the seam a test builds a fixture tree against -------

    def test_run_accepts_a_plain_string_path_as_well_as_a_path_object(self):
        """Criterion 18: run() takes the root a test hands it, either shape."""
        root = self._base()
        (root / "skills" / "epsilon").mkdir()
        from_path, _ = check_roles.run(root)
        from_str, _ = check_roles.run(str(root))
        self.assertEqual(from_path, from_str)

    # -- 20: the real tree, checked, reports nothing --------------------------

    def test_real_container_root_has_no_failures_or_questions(self):
        """Criterion 20: this is the regression check on the actual tree."""
        failures, questions = check_roles.run(WORKBENCH_ROOT)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    # -- 21: the docstring and scripts/README.md describe the check as it runs

    def test_docstring_names_the_exemption_set_not_a_first_party_allowlist(self):
        """Criterion 21: the module docstring describes THIRD_PARTY_SKILLS,
        and neither it nor scripts/README.md claims the name check is limited
        to a list of skills the practice wrote."""
        docstring = check_roles.__doc__ or ""
        self.assertIn("THIRD_PARTY_SKILLS", docstring)
        readme = (WORKBENCH_ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        for text in (docstring, readme):
            self.assertNotIn("FIRST_PARTY_SKILLS", text)

    # -- new defect 1: a SKILL.md that is a directory or a dangling symlink ---

    def test_skill_md_that_is_a_directory_is_reported_as_not_a_readable_file(self):
        """A SKILL.md that is itself a directory used to crash with
        IsADirectoryError. It is now a distinct, named failure."""
        root = self._base()
        (root / "skills" / "foo" / "SKILL.md").mkdir(parents=True)
        failures, _ = check_roles.run(root)
        self.assertIn("skills/foo: SKILL.md is not a readable file", failures)

    def test_skill_md_that_is_a_dangling_symlink_is_reported_as_not_a_readable_file(self):
        """A dangling symlink named SKILL.md used to crash with
        FileNotFoundError. Same message as the directory case."""
        root = self._base()
        target = root / "skills" / "bar"
        target.mkdir(parents=True)
        try:
            (target / "SKILL.md").symlink_to(target / "does-not-exist.md")
        except OSError as exc:
            self.skipTest(f"symlinks not supported here: {exc}")
        failures, _ = check_roles.run(root)
        self.assertIn("skills/bar: SKILL.md is not a readable file", failures)

    def test_absent_skill_md_keeps_its_own_distinct_message(self):
        """An absent file and an unreadable one are deliberately different
        messages, never conflated into one."""
        root = self._base()
        (root / "skills" / "baz").mkdir()
        failures, _ = check_roles.run(root)
        self.assertIn("skills/baz: no SKILL.md", failures)
        self.assertNotIn("skills/baz: SKILL.md is not a readable file", failures)

    def test_role_skills_field_naming_a_directory_reports_the_same_distinction(self):
        """The same fix at the other call site: a role's skills: entry
        naming a directory called SKILL.md does not crash either."""
        root = self._base()
        (root / "skills" / "qux" / "SKILL.md").mkdir(parents=True)
        self._write(root, "agents/builder.md", role_md("builder", skills="qux"))
        failures, _ = check_roles.run(root)
        self.assertIn(
            "agents/builder.md: skill 'qux': skills/qux/SKILL.md is not a readable file",
            failures,
        )

    # -- new defect 2: no trailing newline after the closing fence -----------

    def test_frontmatter_with_no_trailing_newline_after_the_closing_fence_parses(self):
        """A file whose last byte is the closing fence's final '-' is valid.
        It used to be reported as having no frontmatter at all."""
        root = self._base()
        text = "---\nname: nonl\ndescription: does a thing\n---"
        self._write(root, "agents/nonl.md", text)
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    def test_skill_frontmatter_with_no_trailing_newline_also_parses(self):
        """Same fix, same shared parser, on the skill path."""
        root = self._base()
        text = "---\nname: nonl\ndescription: does a thing\n---"
        self._write(root, "skills/nonl/SKILL.md", text)
        failures, _ = check_roles.run(root)
        self.assertEqual(failures, [])

    # -- new defect 3: a byte order mark before the opening fence -------------

    def test_utf8_bom_before_the_opening_fence_gets_its_own_message(self):
        """A byte order mark is named specifically now, not lumped into the
        generic 'no frontmatter' failure."""
        root = self._base()
        text = "﻿---\nname: bombed\ndescription: does a thing\n---\n"
        self._write(root, "agents/bombed.md", text)
        failures, _ = check_roles.run(root)
        self.assertIn(
            "agents/bombed.md: starts with a byte order mark, so --- is not the first thing in it",
            failures,
        )
        self.assertFalse(any(
            f.startswith("agents/bombed.md") and "no frontmatter" in f for f in failures
        ))

    # -- new defect 4: a missing agents/ or skills/ directory -----------------

    def test_missing_agents_directory_is_named_as_a_failure(self):
        """A missing agents/ directory is reported, not silently treated as
        zero role files."""
        root = self._root()
        (root / "skills").mkdir()
        self._write(root, "scripts/model-registry.txt", FIXTURE_REGISTRY)
        failures, _ = check_roles.run(root)
        self.assertIn("agents: no such directory at the checked root", failures)

    def test_missing_skills_directory_is_named_as_a_failure(self):
        """A missing skills/ directory is reported the same way."""
        root = self._root()
        (root / "agents").mkdir()
        self._write(root, "scripts/model-registry.txt", FIXTURE_REGISTRY)
        failures, _ = check_roles.run(root)
        self.assertIn("skills: no such directory at the checked root", failures)

    def test_root_with_neither_directory_is_two_failures_never_a_clean_pass(self):
        """The worst case: an empty directory used to report '0 failure(s)'
        and exit 0. It is now two named failures."""
        root = self._root()
        self._write(root, "scripts/model-registry.txt", FIXTURE_REGISTRY)
        failures, questions = check_roles.run(root)
        self.assertEqual(
            failures,
            [
                "agents: no such directory at the checked root",
                "skills: no such directory at the checked root",
            ],
        )
        self.assertEqual(questions, [])

    # -- new defect 5: text that is not UTF-8, and a file that cannot be read -

    def test_file_that_is_not_utf8_reports_that_specifically(self):
        """Invalid UTF-8 bytes get their own message, not a generic parse
        failure."""
        root = self._base()
        (root / "agents" / "binary.md").write_bytes(b"\x80\x81\x82 not utf8 at all")
        failures, _ = check_roles.run(root)
        self.assertIn("agents/binary.md: is not UTF-8 text", failures)

    def test_unreadable_file_reports_cannot_be_read_with_the_error_type(self):
        """The OSError branch. A self-referential symlink is unreadable in
        every POSIX environment, root included, unlike a chmod'd file, which
        root can still read, so this is the portable way to force it without
        depending on the runner's privilege level. Skipped where symlinks
        are not supported at all."""
        root = self._base()
        loop = root / "agents" / "loop.md"
        try:
            loop.symlink_to(loop)
        except OSError as exc:
            self.skipTest(f"symlinks not supported here: {exc}")
        failures, _ = check_roles.run(root)
        matches = [f for f in failures if f.startswith("agents/loop.md")]
        self.assertEqual(len(matches), 1)
        self.assertIn("cannot be read,", matches[0])

    # -- the real registry's contents, not the script's logic -----------------

    def test_every_value_in_the_real_registry_carries_a_comment(self):
        """Not a test of check-roles.py: a test of scripts/model-registry.txt
        itself. Every model test above runs against FIXTURE_REGISTRY, so
        nothing else reads the real file. A bare identifier with no comment
        passes the script and tells the next reader neither what it is nor
        where it was confirmed, and this is the only thing that catches one.
        The template ships no values, so this passes with nothing to check,
        and it keeps holding for a cloner who registers their own."""
        text = (WORKBENCH_ROOT / "scripts" / "model-registry.txt").read_text(encoding="utf-8")
        for line in text.splitlines():
            value = line.split("#", 1)[0].strip()
            if not value:
                continue
            self.assertIn(
                "#", line,
                f"registered value '{value}' carries no comment saying what it "
                f"is and where it was confirmed")


    def test_skill_name_over_64_characters_fails(self):
        """Agent Skills spec: name is 1 to 64 characters. A 65-character name fails."""
        root = self._base()
        long_name = "a" * 65
        self._write(root, f"skills/{long_name}/SKILL.md",
                    f"---\nname: {long_name}\ndescription: fine.\n---\n")
        failures, questions = check_roles.run(root)
        self.assertEqual(questions, [])
        self.assertTrue(
            any("over the 64" in f for f in failures),
            f"expected a length failure, got {failures}")

    def test_skill_name_of_exactly_64_characters_passes(self):
        """Agent Skills spec: 64 is allowed, so the boundary must not fail."""
        root = self._base()
        name = "a" * 64
        self._write(root, f"skills/{name}/SKILL.md",
                    f"---\nname: {name}\ndescription: fine.\n---\n")
        failures, questions = check_roles.run(root)
        self.assertEqual(failures, [])
        self.assertEqual(questions, [])

    def test_length_rule_runs_on_exempt_skills_too(self):
        """An exemption covers the name-matches-directory rule and nothing else."""
        exempt = self._exempt()
        root = self._base()
        self._write(root, f"skills/{exempt}/SKILL.md",
                    f"---\nname: {'b' * 65}\ndescription: fine.\n---\n")
        failures, questions = check_roles.run(root)
        self.assertTrue(
            any("over the 64" in f for f in failures),
            f"exempt skill should still fail the length rule, got {failures}")

    # -- defects found by critic on the template sync, 2026-09-11 -----------

    def test_skills_as_a_block_list_is_rejected_by_name(self):
        """One form is accepted, and the others are named rather than parsed.

        A block list used to be dropped silently, which is the failure the
        script exists to prevent. It is not parsed now either: it is reported,
        so the writer is told what to change."""
        root = self._base()
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills:\n  - does-not-exist\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("skills: is a block list" in f for f in failures),
                        f"block form was not reported: {failures}")
        self.assertFalse(any("does-not-exist" in f for f in failures),
                         "an unsupported form must not also be parsed")

    def test_skills_as_a_flow_list_is_rejected_by_name(self):
        """`skills: [a, b]` is reported, not silently half-parsed.

        Splitting on commas alone left the brackets attached and produced a
        false failure against a skill that was present."""
        root = self._base()
        self._write(root, "skills/wiki-query/SKILL.md", skill_md("wiki-query"))
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills: [wiki-query, does-not-exist]\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("skills: is a flow list" in f for f in failures),
                        f"flow form was not reported: {failures}")
        self.assertFalse(any("wiki-query" in f for f in failures),
                         "a present skill must never be reported missing")

    def test_skills_inline_is_the_accepted_form(self):
        """The one declared form parses, and a missing skill in it still fails."""
        root = self._base()
        self._write(root, "skills/wiki-query/SKILL.md", skill_md("wiki-query"))
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills: wiki-query, does-not-exist\n---\n")
        failures, _ = check_roles.run(root)
        self.assertFalse(any("wiki-query/" in f for f in failures),
                         f"a present skill was reported missing: {failures}")
        self.assertTrue(any("skill 'does-not-exist'" in f for f in failures),
                        f"the absent skill was not named: {failures}")

    def test_non_utf8_model_registry_is_a_failure_not_a_traceback(self):
        """load_models caught OSError only, so a UnicodeDecodeError escaped."""
        root = self._base()
        (root / "scripts" / "model-registry.txt").write_bytes(b"\x80\x81")
        failures, questions = check_roles.run(root)
        self.assertTrue(any("not UTF-8" in f for f in failures),
                        f"expected a UTF-8 failure, got {failures}")
        self.assertEqual(questions, [])

    def test_the_exemption_is_keyed_on_third_party_skills_membership(self):
        """Criterion 8, strengthened. The old test only asserted the mismatch
        was absent, so a script keyed on anything else satisfied it. This runs
        one fixture both ways and requires membership to be what changes."""
        name = "an-installed-skill"
        root = self._base()
        self._write(root, f"skills/{name}/SKILL.md", skill_md("some-other-name"))
        before, _ = check_roles.run(root)
        self.assertTrue(any(f"skills/{name}/SKILL.md" in f and "does not match directory" in f
                            for f in before),
                        "the mismatch must fail while the directory is not exempt")
        self._exempt(name)
        after, _ = check_roles.run(root)
        self.assertFalse(any(f"skills/{name}/SKILL.md" in f and "does not match directory" in f
                             for f in after),
                         "the exemption must suppress exactly that failure")

    def test_exempt_helper_restores_the_set(self):
        """_exempt mutates a module global; without the restore it leaks into
        every later test, invisibly."""
        original = set(check_roles.THIRD_PARTY_SKILLS)
        class Inner(unittest.TestCase):
            def runTest(inner):
                inner.addCleanup(lambda: None)
                CheckRolesTest._exempt(inner, "leaked-name")
                self.assertIn("leaked-name", check_roles.THIRD_PARTY_SKILLS)
        Inner().run(unittest.TestResult())
        self.assertEqual(set(check_roles.THIRD_PARTY_SKILLS), original,
                         "the set was not restored after the test finished")

    def test_skills_block_list_after_a_blank_line_is_still_refused(self):
        """Criterion 28. A blank line between the key and its items is valid
        YAML and used to clear the parser's idea of the current key, so the
        items were dropped in silence. The silent drop is the whole defect."""
        root = self._base()
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills:\n\n  - does-not-exist\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("skills:" in f and "block list" in f for f in failures),
                        f"a block list behind a blank line was dropped: {failures}")

    def test_skills_as_a_multi_line_plain_scalar_is_refused(self):
        """Criterion 28. `skills:` then indented plain lines is valid YAML for
        one string. Nothing was read and nothing was said."""
        root = self._base()
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills:\n  wiki-query,\n  does-not-exist\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("runs past its own line" in f for f in failures),
                        f"a multi-line scalar was dropped: {failures}")

    def test_skills_with_a_continuation_line_is_refused_not_half_read(self):
        """Criterion 28, the worst variant: the first line parses, so the file
        looks checked while the continuation is discarded."""
        root = self._base()
        self._write(root, "skills/wiki-query/SKILL.md", skill_md("wiki-query"))
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills: wiki-query,\n  does-not-exist\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("runs past its own line" in f for f in failures),
                        f"a continuation line was half-read: {failures}")
        self.assertFalse(any("skill 'wiki-query'" in f for f in failures),
                         "a refused form must not also be parsed")

    def test_empty_flow_list_says_delete_the_line(self):
        """Criterion 29. `skills: []` declares no skills and loses nothing, so
        telling the writer to comma-separate it is advice they cannot take."""
        root = self._base()
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills: []\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("is empty. Delete the line." in f for f in failures),
                        f"expected the delete-the-line message, got {failures}")

    def test_a_trailing_bracket_alone_is_refused(self):
        """Criterion 29. Detection is on either bracket, not both. Testing only
        the balanced form let `or` become `and` with the suite still green."""
        root = self._base()
        self._write(root, "agents/alpha.md",
                    "---\nname: alpha\ndescription: x\nskills: wiki-query]\n---\n")
        failures, _ = check_roles.run(root)
        self.assertTrue(any("flow list" in f for f in failures),
                        f"a trailing bracket was not refused: {failures}")

    def test_a_quoted_inline_skill_name_has_its_quotes_stripped(self):
        """Criterion 28. Without this the quote stripping could be deleted and
        the suite stayed green, while `skills: 'wiki-query'` produced a false
        failure naming a skill that is present."""
        root = self._base()
        self._write(root, "skills/wiki-query/SKILL.md", skill_md("wiki-query"))
        for quoted in ("'wiki-query'", '"wiki-query"'):
            self._write(root, "agents/alpha.md",
                        f"---\nname: alpha\ndescription: x\nskills: {quoted}\n---\n")
            failures, _ = check_roles.run(root)
            self.assertEqual(failures, [], f"{quoted} should resolve to wiki-query")

if __name__ == "__main__":
    unittest.main()
