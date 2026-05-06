"""
tests/test_validator.py — Unit tests for the blacklist validator.
check_payload() is implemented in Phase 1, so these tests run now.
"""

import pytest
from rcefuscator.core.validator import check_payload


class TestCheckPayload:
    def test_clean_payload_returns_true(self):
        """Payload with no blacklisted chars should return clean."""
        is_clean, found = check_payload("$'\\x69\\x64'", [";", "&"])
        assert is_clean is True
        assert found == []

    def test_dirty_payload_returns_false(self):
        """Payload containing a blacklisted char should not be clean."""
        is_clean, found = check_payload("echo 'aWQ=' | base64 -d | sh", ["|"])
        assert is_clean is False
        assert "|" in found

    def test_empty_blacklist_always_clean(self):
        """Empty blacklist means every payload is clean."""
        is_clean, found = check_payload("any|payload;here", [])
        assert is_clean is True
        assert found == []

    def test_multiple_blacklisted_chars_detected(self):
        """All matching chars should be reported."""
        is_clean, found = check_payload("cmd; ls | grep &", [";", "|", "&"])
        assert is_clean is False
        assert set(found) == {";", "|", "&"}

    def test_validator_detects_dirty_payload(self):
        """Validator must catch a dirty payload — core safety check."""
        is_clean, _ = check_payload("cmd; rm -rf /", [";"])
        assert is_clean is False
