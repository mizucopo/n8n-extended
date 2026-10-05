"""Exercise the release-check workflow's actual conditions and inline scripts.

Only literal step metadata/run blocks are extracted; actionlint validates the YAML.
The fixtures use local Git repositories and mock remote API responses.
"""

import ast
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/check-n8n-extended-release.yml"
TEXT = WORKFLOW.read_text()


def steps():
    result = {}
    for block in re.split(r"^      - name: ", TEXT, flags=re.MULTILINE)[1:]:
        name, _, body = block.partition("\n")
        metadata = dict(re.findall(r"^        (\w+): (.+)$", body, re.MULTILINE))
        script = re.search(
            r"^        run: \|\n((?:          .*\n|\n)*)", body, re.MULTILINE
        )
        if script:
            metadata["run"] = "\n".join(line[10:] for line in script[1].splitlines())
        result[name] = metadata
    return result


STEPS = steps()


def condition(expression, context):
    """Evaluate the workflow's boolean subset using fixture context values."""
    expression = expression.removeprefix("${{").removesuffix("}}").strip()

    def token(match):
        value = match[0]
        if value.startswith("'"):
            return value
        if value in ("true", "false", "null"):
            return {"true": "True", "false": "False", "null": "None"}[value]
        current = context
        for key in value.split("."):
            current = current.get(key) if isinstance(current, dict) else None
        return repr(current)

    expression = re.sub(
        r"'[^']*'|\b(?:true|false|null)\b|\b(?:github|steps)(?:\.\w+)+",
        token,
        expression,
    )
    tree = ast.parse(
        expression.replace("&&", " and ").replace("||", " or "), mode="eval"
    )
    allowed = (
        ast.Expression,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.Compare,
        ast.Eq,
        ast.NotEq,
        ast.Constant,
        ast.Dict,
    )
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ValueError(f"Unsupported workflow condition: {expression}")
    return bool(
        eval(compile(tree, "<workflow condition>", "eval"), {"__builtins__": {}}, {})
    )


class ReleaseCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.repo = self.path / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        (self.repo / "version").write_text("1.2.3\n")
        (self.repo / "revision").write_text("")
        self.commit("base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.head = self.base
        self.output = self.path / "output"
        self.bin = self.path / "bin"
        self.bin.mkdir()
        self.mock("gh", 'printf "%s\\n" "$PR_RESPONSE"\nexit "${API_STATUS:-0}"\n')
        self.mock("curl", 'printf "%s" "${HTTP_STATUS:-404}"\n')

    def mock(self, name, body):
        path = self.bin / name
        path.write_text("#!/usr/bin/env bash\n" + body)
        path.chmod(0o755)

    def git(self, *args, check=True):
        return subprocess.run(
            ["git", *args], cwd=self.repo, capture_output=True, text=True, check=check
        )

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def change(self, name):
        (self.repo / name).write_text("changed\n")
        self.commit(name)
        self.head = self.git("rev-parse", "HEAD").stdout.strip()

    def run_step(self, name, **env):
        self.output.write_text("")
        environment = dict(
            os.environ,
            PATH=f"{self.bin}:{os.environ['PATH']}",
            GITHUB_OUTPUT=str(self.output),
            GITHUB_REPOSITORY="mizucopo/n8n-extended",
            GH_TOKEN="fixture",
            PR_NUMBER="33",
            BASE_SHA=self.base,
            HEAD_SHA=self.head,
            REVISION_HINT="Update revision.",
            RELEASE_TAG="1.2.3",
            IMAGE="mizucopo/n8n-extended:1.2.3",
            PR_RESPONSE=json.dumps({"state": "open", "merged": False}),
        )
        environment.update(env)
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", STEPS[name]["run"]],
            cwd=self.repo,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        outputs = dict(
            line.split("=", 1) for line in self.output.read_text().splitlines()
        )
        return result, outputs

    def event_context(self, action="opened", state="open", merged=False, changes=None):
        return {
            "github": {
                "event": {
                    "action": action,
                    "pull_request": {"state": state, "merged": merged},
                    "changes": changes or {},
                }
            }
        }

    def job_runs(self, **event):
        match = re.search(r"^    if: (.+)$", TEXT, re.MULTILINE)
        return condition(match[1], self.event_context(**event)) if match else True

    def test_closed_and_merged_edits_skip_job(self):
        for merged in (False, True):
            for changes in (
                {"title": {}},
                {"body": {}},
                {"base": {"ref": {"from": "other"}}},
            ):
                with self.subTest(merged=merged, changes=changes):
                    self.assertFalse(
                        self.job_runs(
                            action="edited",
                            state="closed",
                            merged=merged,
                            changes=changes,
                        )
                    )

    def test_event_filter(self):
        for action in ("opened", "synchronize", "reopened"):
            self.assertTrue(self.job_runs(action=action))
        self.assertFalse(
            self.job_runs(action="edited", changes={"title": {"from": "old"}})
        )
        self.assertFalse(
            self.job_runs(action="edited", changes={"body": {"from": "old"}})
        )
        self.assertTrue(
            self.job_runs(action="edited", changes={"base": {"ref": {"from": "other"}}})
        )

    def test_queued_merge_and_closed_rerun_skip_checkout_and_checks(self):
        for merged in (False, True):
            result, outputs = self.run_step(
                "Check current PR state",
                PR_RESPONSE=json.dumps({"state": "closed", "merged": merged}),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(outputs.get("validate"), "false")
            context = {
                "steps": {
                    "pr_state": {"outputs": outputs},
                    "release_changes": {"outputs": {}},
                }
            }
            for name, step in STEPS.items():
                if name != "Check current PR state":
                    with self.subTest(merged=merged, step=name):
                        self.assertIn(
                            "if", step, f"{name} would run after the PR closed"
                        )
                        self.assertFalse(condition(step["if"], context), name)

    def test_open_pr_runs_and_checkout_uses_event_head(self):
        result, outputs = self.run_step("Check current PR state")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("validate"), "true")
        checkout = TEXT.split("      - name: Checkout\n", 1)[1].split(
            "      - name:", 1
        )[0]
        self.assertIn("ref: ${{ github.event.pull_request.head.sha }}", checkout)

    def test_state_lookup_errors_fail(self):
        for env in (
            {"API_STATUS": "1"},
            {"PR_RESPONSE": "not json"},
            {"PR_RESPONSE": "{}"},
        ):
            result, outputs = self.run_step("Check current PR state", **env)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("validate", outputs)

    def test_release_inputs_and_unrelated_changes(self):
        for filename in (
            "version",
            "revision",
            "Dockerfile",
            "scripts/resolve-n8n-extended-tags.sh",
            ".github/scripts/example.sh",
            ".github/workflows/release-n8n-extended.yml",
        ):
            (self.repo / filename).parent.mkdir(parents=True, exist_ok=True)
            self.change(filename)
            result, outputs = self.run_step("Detect release-triggering changes")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(outputs.get("release_changes"), "true", filename)
            self.base = self.head
        self.change("README.md")
        result, outputs = self.run_step("Detect release-triggering changes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("release_changes"), "false")

    def test_old_head_rerun_diffs_event_head(self):
        self.change("version")
        old_head = self.head
        self.git("reset", "--hard", self.base)
        self.change("README.md")
        self.git("checkout", "--detach", old_head)
        result, outputs = self.run_step(
            "Detect release-triggering changes", HEAD_SHA=old_head
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("release_changes"), "true")

    def test_wrong_checkout_fails_before_resolving_tags(self):
        self.change("version")
        result, outputs = self.run_step(
            "Detect release-triggering changes", HEAD_SHA=self.base
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Checkout does not match", result.stderr)
        self.assertNotIn("release_changes", outputs)

    def test_squash_merge_deleted_head_reproduces_old_diff_failure(self):
        self.git("checkout", "-qb", "pr")
        self.change("version")
        self.git("checkout", "-q", "main")
        self.git("merge", "--squash", "pr")
        self.commit("squash")
        self.git("branch", "-D", "pr")
        clone = self.path / "clone"
        subprocess.run(
            ["git", "clone", "-q", "--no-local", str(self.repo), str(clone)], check=True
        )
        self.repo = clone
        missing = self.git("cat-file", "-e", self.head, check=False)
        self.assertNotEqual(missing.returncode, 0)
        original_diff = self.git(
            "diff", "--quiet", f"{self.base}...{self.head}", check=False
        )
        self.assertEqual(original_diff.returncode, 128)
        self.assertIn("Invalid symmetric difference expression", original_diff.stderr)
        result, outputs = self.run_step(
            "Check current PR state",
            PR_RESPONSE=json.dumps({"state": "closed", "merged": True}),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("validate"), "false")

    def test_missing_commits_and_merge_base_fail_with_cause(self):
        for role in ("BASE_SHA", "HEAD_SHA"):
            result, outputs = self.run_step(
                "Detect release-triggering changes", **{role: "f" * 40}
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Could not fetch", result.stderr)
            self.assertNotIn("release_changes", outputs)
        self.git("checkout", "--orphan", "unrelated")
        self.commit("unrelated")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        result, outputs = self.run_step("Detect release-triggering changes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No merge base", result.stderr)
        self.assertNotIn("release_changes", outputs)

    def test_fetches_missing_base_commit(self):
        self.git("checkout", "-qb", "pr")
        self.change("version")
        self.git("checkout", "main")
        self.change("README.md")
        self.base = self.head
        self.head = self.git("rev-parse", "pr").stdout.strip()
        remote = self.repo
        clone = self.path / "single-branch"
        subprocess.run(
            [
                "git",
                "clone",
                "-q",
                "--single-branch",
                "--branch",
                "pr",
                "--no-local",
                str(remote),
                str(clone),
            ],
            check=True,
        )
        self.repo = clone
        self.assertNotEqual(
            self.git("cat-file", "-e", self.base, check=False).returncode, 0
        )
        result, outputs = self.run_step("Detect release-triggering changes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("release_changes"), "true")

    def test_duplicate_git_tag_still_fails(self):
        self.git("remote", "add", "origin", str(self.repo))
        self.git("tag", "1.2.3")
        result, _ = self.run_step("Check git tag")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)

    def test_docker_tag_duplicate_available_and_error(self):
        for status, expected in (("200", 1), ("404", 0), ("500", 1)):
            result, _ = self.run_step("Check Docker Hub tag", HTTP_STATUS=status)
            self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
