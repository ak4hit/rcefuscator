"""
validator.py — Blacklist checker & payload verifier for rcefuscator.
Implemented in Phase 2. Stub present for Phase 1 structure validation.
"""

from typing import List, Tuple


def check_payload(payload: str, blacklist: List[str]) -> Tuple[bool, List[str]]:
    """
    Check whether a payload contains any blacklisted characters.

    Args:
        payload:   The generated obfuscation payload string.
        blacklist: List of characters/strings that are blocked by the target WAF.

    Returns:
        Tuple of (is_clean: bool, found_chars: List[str])
        - is_clean is True if no blacklisted chars are found.
        - found_chars contains every blacklisted character present in the payload.
    """
    found = [char for char in blacklist if char in payload]
    return (len(found) == 0, found)
