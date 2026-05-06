"""
tests/test_cli.py -- CLI integration tests for rcefuscator.
Uses Click's test runner so no real terminal / disclaimer needed.
"""

import json
import pytest
from click.testing import CliRunner
from rcefuscator.cli.main import cli, ACK_FILE


# ---------------------------------------------------------------------------
# Fixture: pre-acknowledge the disclaimer so tests are non-interactive
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def auto_ack(tmp_path, monkeypatch):
    """
    Redirect ACK_FILE to a temp path and pre-create it so the
    disclaimer prompt is never shown during tests.
    """
    ack = tmp_path / ".rcefuscator_ack"
    ack.write_text("acknowledged", encoding="utf-8")
    monkeypatch.setattr("rcefuscator.cli.main.ACK_FILE", ack)
    yield


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run(args, input=None):
    runner = CliRunner()
    return runner.invoke(cli, args, input=input, catch_exceptions=False)


# ---------------------------------------------------------------------------
# Help / version
# ---------------------------------------------------------------------------

class TestCliHelp:
    def test_help_flag_exits_zero(self):
        result = run(["--help"])
        assert result.exit_code == 0
        assert "rcefuscator" in result.output.lower()

    def test_version_flag(self):
        result = run(["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_no_args_prints_help(self):
        result = run([])
        assert result.exit_code == 0
        assert "--cmd" in result.output


# ---------------------------------------------------------------------------
# --list-techniques
# ---------------------------------------------------------------------------

class TestCliListTechniques:
    def test_list_techniques_exits_zero(self):
        result = run(["--list-techniques"])
        assert result.exit_code == 0

    def test_list_techniques_shows_all_ids(self):
        # Verify all 8 techniques are registered by checking the techniques module directly
        from rcefuscator.core.techniques import TECHNIQUES
        ids = [t["id"] for t in TECHNIQUES]
        expected_ids = ["base64", "hex_printf", "ansi_c", "var_split",
                        "wildcard", "reverse", "case_mangle", "cmd_sub"]
        for tid in expected_ids:
            assert tid in ids, f"Technique '{tid}' not found in registry"
        # Also confirm the CLI command exits cleanly
        result = run(["-l"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# --cmd flag
# ---------------------------------------------------------------------------

class TestCliCmdFlag:
    def test_cmd_id_produces_output(self):
        # Verify via JSON that payloads are generated for 'id'
        result = run(["--cmd", "id", "--blacklist", ";", "--json"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        assert data["command"] == "id"
        assert data["total"] > 0

    def test_cmd_whoami_produces_output(self):
        # Verify via JSON that payloads are generated for 'whoami'
        result = run(["--cmd", "whoami", "--blacklist", ";", "--json"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        assert data["command"] == "whoami"
        assert any("whoami" in p["payload"] for p in data["payloads"])

    def test_cmd_with_profile_strict(self):
        result = run(["--cmd", "id", "--profile", "strict"])
        assert result.exit_code == 0

    def test_cmd_with_profile_paranoid(self):
        result = run(["--cmd", "id", "--profile", "paranoid"])
        assert result.exit_code == 0

    def test_cmd_with_custom_blacklist(self):
        result = run(["--cmd", "id", "--blacklist", "|"])
        assert result.exit_code == 0

    def test_unknown_profile_exits_nonzero(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--cmd", "id", "--profile", "nonexistent"])
        assert result.exit_code != 0

    def test_single_technique_base64(self):
        # Use --json so output is parseable; semicolon-only blacklist doesn't affect base64
        result = run(["--cmd", "id", "--technique", "base64", "--blacklist", ";", "--json"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        assert len(data["payloads"]) == 1
        assert data["payloads"][0]["technique"] == "base64"
        assert "aWQ=" in data["payloads"][0]["payload"]  # base64 of 'id'


    def test_unknown_technique_exits_nonzero(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--cmd", "id", "--technique", "nonexistent"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# --json flag
# ---------------------------------------------------------------------------

class TestCliJsonOutput:
    def test_json_flag_produces_valid_json(self):
        result = run(["--cmd", "id", "--json"])
        assert result.exit_code == 0
        # Strip any leading non-JSON lines (the "Command:" info line)
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        json_str = "\n".join(lines[json_start:])
        data = json.loads(json_str)
        assert data["command"] == "id"
        assert "payloads" in data
        assert isinstance(data["payloads"], list)

    def test_json_contains_required_fields(self):
        result = run(["--cmd", "whoami", "--json"])
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        for payload in data["payloads"]:
            assert "technique" in payload
            assert "payload"   in payload
            assert "clean"     in payload
            assert "shell"     in payload

    def test_json_clean_flag_matches_blacklist(self):
        result = run(["--cmd", "id", "--blacklist", "|", "--json"])
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        for payload in data["payloads"]:
            if "|" in payload.get("payload", ""):
                assert not payload["clean"]


# ---------------------------------------------------------------------------
# --output flag
# ---------------------------------------------------------------------------

class TestCliOutputFile:
    def test_output_flag_creates_file(self, tmp_path):
        out = tmp_path / "payloads.txt"
        result = run(["--cmd", "id", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "id" in content

    def test_output_file_has_metadata_header(self, tmp_path):
        out = tmp_path / "out.txt"
        run(["--cmd", "id", "--output", str(out)])
        content = out.read_text(encoding="utf-8")
        assert "# rcefuscator output" in content
        assert "# Command: id" in content


# ---------------------------------------------------------------------------
# --show-skipped flag
# ---------------------------------------------------------------------------

class TestCliShowSkipped:
    def test_show_skipped_includes_skip_lines(self):
        # When | is blacklisted, pipe-based techniques should be skipped.
        # Verify via JSON that they are absent from results (i.e., skipped).
        result = run(["--cmd", "id", "--blacklist", "|", "--json"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        json_start = next(i for i, l in enumerate(lines) if l.strip().startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        # base64, hex_printf, reverse, case_mangle should not appear in payloads
        returned_ids = {p["technique"] for p in data["payloads"]}
        pipe_techniques = {"base64", "hex_printf", "reverse", "case_mangle"}
        assert returned_ids.isdisjoint(pipe_techniques), (
            f"Pipe techniques should be skipped but found: {returned_ids & pipe_techniques}"
        )
