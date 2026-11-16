#!/usr/bin/env python3
"""Check inline JavaScript syntax in every HTML file using Node's parser.

This only parses scripts. It never runs application code or reads browser data.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv"}
JS_TYPES = {
    "",
    "text/javascript",
    "application/javascript",
    "text/ecmascript",
    "application/ecmascript",
}
MODULE_TYPE = "module"


class InlineScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.current: dict[str, object] | None = None
        self.scripts: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attr = {name.lower(): value for name, value in attrs}
        script_type = (attr.get("type") or "").split(";", 1)[0].strip().lower()
        is_module = script_type == MODULE_TYPE
        is_javascript = is_module or script_type in JS_TYPES
        self.current = None
        if "src" not in attr and is_javascript:
            self.current = {
                "line": self.getpos()[0],
                "module": is_module,
                "parts": [],
            }

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            parts = self.current["parts"]
            assert isinstance(parts, list)
            parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.current is not None:
            self.scripts.append(self.current)
            self.current = None


def iter_html_files(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name.lower().endswith(".html"):
                yield Path(current) / name


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = list(iter_html_files(root))
    if not files:
        print("No HTML files found.", file=sys.stderr)
        return 1

    failures = 0
    checked_scripts = 0
    with tempfile.TemporaryDirectory(prefix="html-inline-js-") as temp_dir:
        temp_root = Path(temp_dir)
        for html_path in files:
            try:
                source = html_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                print(f"{html_path}: cannot read as UTF-8: {exc}", file=sys.stderr)
                failures += 1
                continue

            parser = InlineScriptParser()
            try:
                parser.feed(source)
                parser.close()
            except Exception as exc:
                print(f"{html_path}: HTML parser error: {exc}", file=sys.stderr)
                failures += 1
                continue

            for index, item in enumerate(parser.scripts, start=1):
                parts = item["parts"]
                assert isinstance(parts, list)
                code = "".join(parts)
                if not code.strip():
                    continue

                checked_scripts += 1
                ext = ".mjs" if item["module"] else ".js"
                temp_script = temp_root / f"script-{checked_scripts}{ext}"
                temp_script.write_text(code, encoding="utf-8")
                result = subprocess.run(
                    ["node", "--check", str(temp_script)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                if result.returncode:
                    failures += 1
                    line = item["line"]
                    print(
                        f"{html_path}: inline JavaScript block {index} "
                        f"(starts near line {line}) has a syntax error:",
                        file=sys.stderr,
                    )
                    if result.stderr:
                        print(result.stderr.rstrip(), file=sys.stderr)
                    if result.stdout:
                        print(result.stdout.rstrip(), file=sys.stderr)

    if failures:
        print(
            f"Inline JavaScript check failed: {failures} problem(s), "
            f"{checked_scripts} block(s) checked.",
            file=sys.stderr,
        )
        return 1

    print(f"Inline JavaScript syntax OK: {checked_scripts} block(s) checked across {len(files)} HTML file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
