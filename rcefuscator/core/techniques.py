"""
techniques.py — Technique registry & metadata for rcefuscator.

Each entry in TECHNIQUES declares:
  - id:          unique slug (used by --technique flag)
  - name:        human-readable label
  - function:    callable from encoder.py
  - uses_chars:  chars the payload itself emits (used for auto-skip)
  - shell:       target shell context
  - description: one-line summary
"""

from rcefuscator.core.encoder import (
    base64_encode,
    hex_encode,
    ansi_c_quote,
    var_split,
    wildcard_expand,
    reverse_encode,
    case_mangle,
    cmd_substitution,
)

# ---------------------------------------------------------------------------
# WAF Profile presets
# ---------------------------------------------------------------------------
WAF_PROFILES = {
    "moderate": [";", "|", "&", "`"],
    "strict":   [";", "|", "&", "$", "`", "(", ")", "<", ">", " "],
    "paranoid": [";", "|", "&", "$", "`", "(", ")", "<", ">", " ", "'", '"', "\\"],
    "custom":   [],  # Populated at runtime via --blacklist flag
}

# ---------------------------------------------------------------------------
# Technique registry
# ---------------------------------------------------------------------------
TECHNIQUES = [
    {
        "id":          "base64",
        "name":        "Base64 Encoding",
        "function":    base64_encode,
        "uses_chars":  ["|"],
        "shell":       "bash/sh",
        "description": "Encodes command as base64, decoded at runtime: echo '...'|base64 -d|sh",
    },
    {
        "id":          "hex_printf",
        "name":        "Hex Encoding (printf + xxd)",
        "function":    hex_encode,
        "uses_chars":  ["|"],
        "shell":       "bash/sh",
        "description": "Hex-encodes command, decodes via printf/xxd pipeline",
    },
    {
        "id":          "ansi_c",
        "name":        "ANSI-C Quoting ($'\\x..')",
        "function":    ansi_c_quote,
        "uses_chars":  ["$", "'"],
        "shell":       "bash",
        "description": "Converts chars to \\xHH inside $'...' — no pipes, cleanest technique",
    },
    {
        "id":          "var_split",
        "name":        "Variable Splitting",
        "function":    var_split,
        "uses_chars":  ["$", "'"],
        "shell":       "bash/sh",
        "description": "Splits command into 2-char chunks assigned to vars, joined via $'\\n' newline separator",
    },
    {
        "id":          "wildcard",
        "name":        "Wildcard / Glob Expansion",
        "function":    wildcard_expand,
        "uses_chars":  [],
        "shell":       "bash/sh",
        "description": "Replaces binary path components with ??? glob patterns — zero special chars",
    },
    {
        "id":          "reverse",
        "name":        "Reverse String",
        "function":    reverse_encode,
        "uses_chars":  ["|"],
        "shell":       "bash/sh",
        "description": "Reverses command and decodes at runtime: echo '...'|rev|sh",
    },
    {
        "id":          "case_mangle",
        "name":        "Case Manipulation",
        "function":    case_mangle,
        "uses_chars":  ["|"],
        "shell":       "bash/sh",
        "description": "Uppercases command, lowercases via tr pipeline at runtime",
    },
    {
        "id":          "cmd_sub",
        "name":        "Command Substitution $(…)",
        "function":    cmd_substitution,
        "uses_chars":  ["$", "(", ")"],
        "shell":       "bash",
        "description": "Wraps hex-encoded printf call in $(...) — executes inline",
    },
]


def get_technique_by_id(technique_id: str) -> dict | None:
    """Look up a technique entry by its slug ID. Returns None if not found."""
    return next((t for t in TECHNIQUES if t["id"] == technique_id), None)


def run_technique(technique: dict, cmd: str, blacklist: list) -> dict:
    """
    Execute a single technique against a command and return a result dict.

    Handles:
    - Wildcard skip when binary is unknown
    - Auto-skip when the technique's own chars are blacklisted
    - Clean/dirty classification via blacklist check

    Returns a result dict with keys:
        id, name, payload, clean, uses_chars, shell, description,
        skipped (bool), skip_reason (str or None)
    """
    from rcefuscator.core.validator import check_payload

    result = {
        "id":          technique["id"],
        "name":        technique["name"],
        "uses_chars":  technique["uses_chars"],
        "shell":       technique["shell"],
        "description": technique["description"],
        "skipped":     False,
        "skip_reason": None,
        "payload":     None,
        "clean":       False,
    }

    # Auto-skip if any of the technique's own required chars are blacklisted
    blocked = [c for c in technique["uses_chars"] if c in blacklist]
    if blocked:
        result["skipped"] = True
        result["skip_reason"] = f"Technique requires {blocked} which are blacklisted"
        return result

    # Call the encoder function
    if technique["id"] == "wildcard":
        payload = technique["function"](cmd)
        if payload is None:
            binary = cmd.split()[0]
            result["skipped"] = True
            result["skip_reason"] = f"Unknown binary path for '{binary}' — add to BINARY_PATHS"
            return result
    else:
        payload = technique["function"](cmd)

    is_clean, found = check_payload(payload, blacklist)

    result["payload"] = payload
    result["clean"] = is_clean
    return result


def run_all_techniques(cmd: str, blacklist: list) -> list[dict]:
    """
    Run every registered technique against the command and return all results.
    Results include both clean and dirty payloads (caller decides what to show).
    """
    return [run_technique(t, cmd, blacklist) for t in TECHNIQUES]
