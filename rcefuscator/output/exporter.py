"""
output/exporter.py — JSON and plain-text file export for rcefuscator.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def build_payload_export(results: list, command: str, waf_profile: str) -> dict:
    """
    Build the full export data structure (used by both JSON and file export).
    """
    payloads = []
    for r in results:
        if r["skipped"]:
            continue
        payloads.append({
            "technique":   r["id"],
            "name":        r["name"],
            "payload":     r["payload"],
            "clean":       r["clean"],
            "uses_chars":  r["uses_chars"],
            "shell":       r["shell"],
            "description": r["description"],
        })

    return {
        "command":      command,
        "waf_profile":  waf_profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total":        len(payloads),
        "clean_count":  sum(1 for p in payloads if p["clean"]),
        "payloads":     payloads,
    }


def export_json(results: list, command: str, waf_profile: str) -> str:
    """
    Serialize payload results to a JSON string.

    Returns:
        Formatted JSON string.
    """
    data = build_payload_export(results, command, waf_profile)
    return json.dumps(data, indent=2)


def export_to_file(results: list, command: str, waf_profile: str, filepath: str) -> int:
    """
    Write plain-text payloads to a file (one per line, with metadata header).

    Returns:
        Number of payloads written.
    """
    data = build_payload_export(results, command, waf_profile)
    path = Path(filepath)

    lines = [
        f"# rcefuscator output",
        f"# Command: {data['command']}",
        f"# WAF Profile: {data['waf_profile']}",
        f"# Generated: {data['generated_at']}",
        f"# Total: {data['total']}  Clean: {data['clean_count']}",
        "",
    ]

    for p in data["payloads"]:
        clean_label = "CLEAN" if p["clean"] else "FLAGGED"
        lines.append(f"# [{clean_label}] {p['name']} | Shell: {p['shell']}")
        lines.append(p["payload"])
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return data["total"]
