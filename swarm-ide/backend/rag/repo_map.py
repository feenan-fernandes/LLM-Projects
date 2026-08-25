"""
repo_map.py  — Phase 3
Tree-sitter powered repository symbol map.
Parses workspace Python files, extracts class/function/method signatures,
ranks them by PageRank (cross-file reference density), and emits a compact
token-budgeted map injected into the Orchestrator's context.

Inspired by Aider's repomap.py and RepoGraph (arXiv:2410.14684).
"""
import os
import sqlite3
import tempfile
from pathlib import Path
from collections import defaultdict

try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
    PY_LANGUAGE = Language(tspython.language())
except Exception:
    TREE_SITTER_AVAILABLE = False

# Max tokens (chars / 4 ≈ tokens) we'll put in the map
MAX_MAP_CHARS = 2000


# ---------------------------------------------------------------------------
# AST extraction
# ---------------------------------------------------------------------------

def _extract_symbols(source_code: str, filepath: str) -> list[dict]:
    """Returns list of {name, kind, line, file} from a Python source file."""
    if not TREE_SITTER_AVAILABLE:
        return _extract_symbols_regex(source_code, filepath)

    try:
        parser = Parser(PY_LANGUAGE)
        tree = parser.parse(source_code.encode())
    except Exception:
        return _extract_symbols_regex(source_code, filepath)

    symbols = []

    def walk(node, parent_class=None):
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                symbols.append({"name": name, "kind": "class", "line": node.start_point[0] + 1, "file": filepath, "parent": None})
                for child in node.children:
                    walk(child, parent_class=name)
        elif node.type in ("function_definition", "async_function_definition"):
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            returns_node = node.child_by_field_name("return_type")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                params = source_code[params_node.start_byte:params_node.end_byte] if params_node else "()"
                ret = " -> " + source_code[returns_node.start_byte:returns_node.end_byte] if returns_node else ""
                symbols.append({
                    "name": name,
                    "kind": "method" if parent_class else "function",
                    "signature": f"def {name}{params}{ret}",
                    "line": node.start_point[0] + 1,
                    "file": filepath,
                    "parent": parent_class,
                })
        else:
            for child in node.children:
                walk(child, parent_class=parent_class)

    walk(tree.root_node)
    return symbols


def _extract_symbols_regex(source_code: str, filepath: str) -> list[dict]:
    """Regex fallback when tree-sitter is unavailable."""
    import re
    symbols = []
    for i, line in enumerate(source_code.splitlines(), 1):
        cm = re.match(r"^class\s+(\w+)", line)
        if cm:
            symbols.append({"name": cm.group(1), "kind": "class", "line": i, "file": filepath, "parent": None, "signature": line.strip()})
        fm = re.match(r"^\s+def\s+(\w+)\(", line)
        if fm:
            symbols.append({"name": fm.group(1), "kind": "method", "line": i, "file": filepath, "parent": None, "signature": line.strip()})
        tfm = re.match(r"^def\s+(\w+)\(", line)
        if tfm:
            symbols.append({"name": tfm.group(1), "kind": "function", "line": i, "file": filepath, "parent": None, "signature": line.strip()})
    return symbols


# ---------------------------------------------------------------------------
# PageRank scoring
# ---------------------------------------------------------------------------

def _score_symbols(all_symbols: list[dict], all_source: dict[str, str]) -> dict[str, float]:
    """
    Simple PageRank-style scoring: a symbol gets +1 for each file that references its name.
    Returns {symbol_name: score}.
    """
    name_to_score = defaultdict(float)
    all_names = {s["name"] for s in all_symbols}
    for filepath, source in all_source.items():
        for name in all_names:
            if name in source:
                name_to_score[name] += 1.0
    return name_to_score


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_repo_map(workspace_dir: str, max_chars: int = MAX_MAP_CHARS) -> str:
    """
    Scans workspace_dir for Python files, extracts symbols, ranks by reference count,
    and returns a compact string map suitable for Orchestrator context injection.
    """
    workspace = Path(workspace_dir)
    py_files = list(workspace.rglob("*.py"))

    if not py_files:
        return "[repo_map: no Python files found in workspace]"

    all_symbols = []
    all_source = {}

    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            all_source[str(f)] = src
            syms = _extract_symbols(src, str(f.relative_to(workspace)))
            all_symbols.extend(syms)
        except Exception:
            continue

    scores = _score_symbols(all_symbols, all_source)

    # Sort symbols: by file then by score descending
    all_symbols.sort(key=lambda s: (-scores.get(s["name"], 0), s["file"], s["line"]))

    # Group by file
    by_file = defaultdict(list)
    for s in all_symbols:
        by_file[s["file"]].append(s)

    # Render map
    lines = ["[REPO MAP]"]
    chars_used = len(lines[0])

    for filepath, syms in by_file.items():
        file_header = f"\n{filepath}"
        if chars_used + len(file_header) > max_chars:
            lines.append("\n... (map truncated at budget)")
            break
        lines.append(file_header)
        chars_used += len(file_header)

        current_class = None
        for s in syms:
            if s["kind"] == "class":
                entry = f"\n  class {s['name']}:              [L{s['line']}]"
                current_class = s["name"]
            elif s["kind"] == "method":
                sig = s.get("signature", f"def {s['name']}()")
                entry = f"\n    {sig}   [L{s['line']}]"
            else:
                sig = s.get("signature", f"def {s['name']}()")
                entry = f"\n  {sig}   [L{s['line']}]"

            if chars_used + len(entry) > max_chars:
                lines.append("\n  ...")
                break
            lines.append(entry)
            chars_used += len(entry)

    return "".join(lines)
