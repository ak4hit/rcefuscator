#!/usr/bin/env bash
# =============================================================================
# tests/functional_test.sh
# rcefuscator -- Functional Payload Validation
#
# PURPOSE:
#   Run each generated payload inside a bash shell and confirm it produces
#   output containing "uid=" (the expected output of the `id` command).
#
# USAGE:
#   # Run inside Docker:
#   docker run --rm -it -v "$(pwd)":/app ubuntu:22.04 bash /app/tests/functional_test.sh
#
#   # Or directly on a Linux system with bash:
#   bash tests/functional_test.sh
#
# REQUIREMENTS:
#   - bash 4+, base64, xxd, printf, rev, tr, python3 (for payload generation)
#   - Run from the rcefuscator project root
# =============================================================================

set -euo pipefail

PASS=0
FAIL=0
SKIP=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

CMD="id"
EXPECTED="uid="

echo "============================================================"
echo " rcefuscator -- Functional Payload Validation"
echo " Target command: $CMD"
echo " Expected output contains: $EXPECTED"
echo "============================================================"
echo ""

run_test() {
    local name="$1"
    local payload="$2"

    # Evaluate the payload inside bash and capture output
    output=$(bash -c "$payload" 2>/dev/null || true)

    if echo "$output" | grep -q "$EXPECTED"; then
        echo -e "${GREEN}[PASS]${RESET} $name"
        echo "       Payload : $payload"
        echo "       Output  : $output"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}[FAIL]${RESET} $name"
        echo "       Payload : $payload"
        echo "       Output  : ${output:-<empty>}"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}

skip_test() {
    local name="$1"
    local reason="$2"
    echo -e "${YELLOW}[SKIP]${RESET} $name -- $reason"
    SKIP=$((SKIP + 1))
    echo ""
}

# ---------------------------------------------------------------------------
# Technique 1: Base64 Encoding
# ---------------------------------------------------------------------------
B64=$(echo -n "$CMD" | base64)
run_test "Base64 Encoding" "echo '${B64}'|base64 -d|sh"

# ---------------------------------------------------------------------------
# Technique 2: Hex Encoding (printf + xxd)
# ---------------------------------------------------------------------------
HEX=$(echo -n "$CMD" | xxd -p | sed 's/../\\x&/g')
run_test "Hex Encoding (printf + xxd)" "printf '${HEX}'|xxd -p -r|sh"

# ---------------------------------------------------------------------------
# Technique 3: ANSI-C Quoting
# ---------------------------------------------------------------------------
ANSI=$(echo -n "$CMD" | od -A n -t x1 | tr -d ' \n' | sed 's/../\\x&/g')
run_test "ANSI-C Quoting" "\$'${ANSI}'"

# ---------------------------------------------------------------------------
# Technique 4: Variable Splitting
# ---------------------------------------------------------------------------
run_test "Variable Splitting (id)" "_a=i;_b=d;\$_a\$_b"

# ---------------------------------------------------------------------------
# Technique 5: Wildcard / Glob Expansion
# ---------------------------------------------------------------------------
if [ -f /usr/bin/id ]; then
    run_test "Wildcard Glob (/usr/bin/id)" "/???/???/id"
elif [ -f /bin/id ]; then
    run_test "Wildcard Glob (/bin/id)" "/???/id"
else
    skip_test "Wildcard Glob" "Cannot locate id binary"
fi

# ---------------------------------------------------------------------------
# Technique 6: Reverse String
# ---------------------------------------------------------------------------
REVERSED=$(echo -n "$CMD" | rev)
run_test "Reverse String" "echo '${REVERSED}'|rev|sh"

# ---------------------------------------------------------------------------
# Technique 7: Case Manipulation
# ---------------------------------------------------------------------------
UPPER=$(echo "$CMD" | tr 'a-z' 'A-Z')
run_test "Case Manipulation" "echo '${UPPER}'|tr 'A-Z' 'a-z'|sh"

# ---------------------------------------------------------------------------
# Technique 8: Command Substitution
# ---------------------------------------------------------------------------
HEX2=$(echo -n "$CMD" | od -A n -t x1 | tr -d ' \n' | sed 's/../\\x&/g')
run_test "Command Substitution" "\$(printf '${HEX2}')"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "============================================================"
echo " Results: ${PASS} passed | ${FAIL} failed | ${SKIP} skipped"
echo "============================================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
