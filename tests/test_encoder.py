"""
tests/test_encoder.py — Unit tests for all obfuscation techniques.
"""

import base64
import pytest
from rcefuscator.core.encoder import (
    base64_encode,
    hex_encode,
    ansi_c_quote,
    var_split,
    wildcard_expand,
    reverse_encode,
    case_mangle,
    cmd_substitution,
    BINARY_PATHS,
)
from rcefuscator.core.validator import check_payload
from rcefuscator.core.techniques import TECHNIQUES, run_all_techniques


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def assert_no_pipe(payload: str):
    assert "|" not in payload, f"Expected no pipe in payload: {payload}"


# ---------------------------------------------------------------------------
# Technique 1 — Base64
# ---------------------------------------------------------------------------

class TestBase64Encode:
    def test_output_not_empty(self):
        assert base64_encode("id") != ""

    def test_payload_structure_valid(self):
        p = base64_encode("id")
        assert "base64 -d" in p
        assert "sh" in p

    def test_correct_b64_value(self):
        p = base64_encode("id")
        expected_b64 = base64.b64encode(b"id").decode()
        assert expected_b64 in p

    def test_multiword_command(self):
        p = base64_encode("cat /etc/passwd")
        assert base64.b64encode(b"cat /etc/passwd").decode() in p


# ---------------------------------------------------------------------------
# Technique 2 — Hex Encoding
# ---------------------------------------------------------------------------

class TestHexEncode:
    def test_output_not_empty(self):
        assert hex_encode("id") != ""

    def test_payload_contains_hex_chars(self):
        p = hex_encode("id")
        assert "\\x69" in p  # 'i' = 0x69
        assert "\\x64" in p  # 'd' = 0x64

    def test_payload_structure_valid(self):
        p = hex_encode("id")
        assert "printf" in p
        assert "xxd" in p
        assert "sh" in p


# ---------------------------------------------------------------------------
# Technique 3 — ANSI-C Quoting
# ---------------------------------------------------------------------------

class TestAnsiCQuote:
    def test_output_not_empty(self):
        assert ansi_c_quote("id") != ""

    def test_no_pipes_in_payload(self):
        p = ansi_c_quote("id")
        assert_no_pipe(p)

    def test_wrapped_in_dollar_quote(self):
        p = ansi_c_quote("id")
        assert p.startswith("$'")
        assert p.endswith("'")

    def test_contains_hex_sequences(self):
        p = ansi_c_quote("id")
        assert "\\x69" in p
        assert "\\x64" in p


# ---------------------------------------------------------------------------
# Technique 4 — Variable Splitting
# ---------------------------------------------------------------------------

class TestVarSplit:
    def test_output_not_empty(self):
        assert var_split("id") != ""

    def test_contains_dollar_ref(self):
        p = var_split("id")
        assert "$" in p

    def test_two_char_chunks(self):
        p = var_split("whoami")
        # Should contain wh, oa, mi as chunks
        assert "wh" in p
        assert "oa" in p
        assert "mi" in p

    def test_single_char_command(self):
        p = var_split("w")
        assert "w" in p


# ---------------------------------------------------------------------------
# Technique 5 — Wildcard / Glob Expansion
# ---------------------------------------------------------------------------

class TestWildcardExpand:
    def test_known_binary_returns_payload(self):
        p = wildcard_expand("id")
        assert p is not None
        assert "???" in p
        assert "id" in p

    def test_unknown_binary_returns_none(self):
        p = wildcard_expand("notabinary")
        assert p is None

    def test_no_special_chars_in_payload(self):
        p = wildcard_expand("id")
        for char in ["|", "&", ";", "$", "`"]:
            assert char not in p, f"Unexpected char '{char}' in wildcard payload"

    def test_whoami_glob(self):
        p = wildcard_expand("whoami")
        assert p is not None
        assert "whoami" in p


# ---------------------------------------------------------------------------
# Technique 6 — Reverse String
# ---------------------------------------------------------------------------

class TestReverseEncode:
    def test_output_not_empty(self):
        assert reverse_encode("id") != ""

    def test_payload_structure_valid(self):
        p = reverse_encode("id")
        assert "rev" in p
        assert "sh" in p

    def test_reversed_string_present(self):
        p = reverse_encode("id")
        assert "di" in p  # 'id' reversed


# ---------------------------------------------------------------------------
# Technique 7 — Case Manipulation
# ---------------------------------------------------------------------------

class TestCaseMangle:
    def test_output_not_empty(self):
        assert case_mangle("id") != ""

    def test_command_uppercased(self):
        p = case_mangle("id")
        assert "ID" in p

    def test_payload_structure_valid(self):
        p = case_mangle("id")
        assert "tr" in p
        assert "A-Z" in p
        assert "a-z" in p


# ---------------------------------------------------------------------------
# Technique 8 — Command Substitution
# ---------------------------------------------------------------------------

class TestCmdSubstitution:
    def test_output_not_empty(self):
        assert cmd_substitution("id") != ""

    def test_wrapped_in_dollar_parens(self):
        p = cmd_substitution("id")
        assert p.startswith("$(")
        assert p.endswith(")")

    def test_contains_printf(self):
        p = cmd_substitution("id")
        assert "printf" in p


# ---------------------------------------------------------------------------
# Technique registry checks
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_registry_has_all_8_techniques(self):
        assert len(TECHNIQUES) == 8

    def test_all_techniques_have_required_keys(self):
        required = {"id", "name", "function", "uses_chars", "shell", "description"}
        for t in TECHNIQUES:
            assert required.issubset(t.keys()), f"Technique missing keys: {t}"

    def test_run_all_techniques_returns_8_results(self):
        results = run_all_techniques("id", [])
        assert len(results) == 8

    def test_run_all_with_empty_blacklist_no_skips(self):
        results = run_all_techniques("id", [])
        # Wildcard for 'id' exists, so none should be skipped
        skipped = [r for r in results if r["skipped"]]
        assert len(skipped) == 0

    def test_pipe_blacklist_skips_pipe_techniques(self):
        results = run_all_techniques("id", ["|"])
        pipe_techniques = {"base64", "hex_printf", "reverse", "case_mangle"}
        for r in results:
            if r["id"] in pipe_techniques:
                assert r["skipped"], f"Expected {r['id']} to be skipped when | is blacklisted"

    def test_no_blacklisted_chars_in_clean_payload(self):
        blacklist = ["|"]
        results = run_all_techniques("id", blacklist)
        for r in results:
            if r["skipped"] or not r["clean"]:
                continue
            is_clean, found = check_payload(r["payload"], blacklist)
            assert is_clean, f"Payload '{r['payload']}' contains blacklisted chars: {found}"
