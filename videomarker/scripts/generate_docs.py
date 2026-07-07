#!/usr/bin/env python3
"""Auto-generate API reference docs from VDOC's source code.

Usage:
    python scripts/generate_docs.py [--output docs/api]
"""

from __future__ import annotations

import argparse
import ast
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root so we can import vdoc
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vdoc


def get_classes(module) -> List[Tuple[str, type]]:
    return [(n, cls) for n, cls in inspect.getmembers(module, inspect.isclass)
            if cls.__module__ == getattr(module, "__name__", "") or cls.__module__.startswith("vdoc")]


def get_functions(module) -> List[Tuple[str, Any]]:
    return [(n, fn) for n, fn in inspect.getmembers(module, inspect.isfunction)
            if fn.__module__ == getattr(module, "__name__", "") or fn.__module__.startswith("vdoc")]


def format_signature(cls_or_fn) -> str:
    try:
        sig = inspect.signature(cls_or_fn)
        params = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            default = ""
            if param.default is not inspect.Parameter.empty:
                default = f" = {repr(param.default)}"
            annotation = ""
            if param.annotation is not inspect.Parameter.empty:
                ann = param.annotation
                if hasattr(ann, "__name__"):
                    annotation = f": {ann.__name__}"
                else:
                    annotation = f": {str(ann)}"
            params.append(f"{name}{annotation}{default}")
        return f"({', '.join(params)})"
    except (ValueError, TypeError):
        return "(...)"


def get_docstring(obj) -> str:
    doc = inspect.getdoc(obj)
    return doc or ""


def generate_module_docs(module, module_name: str, output_dir: Path, visited: Set[str]) -> None:
    if module_name in visited:
        return
    visited.add(module_name)

    pkg = module_name.split(".")[-1]
    doc_path = output_dir / f"{pkg}.md"
    print(f"  Generating {doc_path.name}...")

    lines = [f"# `{module_name}`", "", get_docstring(module), ""]

    # Submodules
    submodules = []
    for name, submod in inspect.getmembers(module, inspect.ismodule):
        if submod.__name__.startswith("vdoc.") and submod.__name__ != module_name:
            submodules.append(submod.__name__)
    if submodules:
        lines.append("## Submodules")
        lines.append("")
        for sm in sorted(submodules):
            rel = sm.replace(".", "/")
            lines.append(f"- [`{sm}`]({rel.split('/')[-1]}.md)")
        lines.append("")

    # Classes
    classes = get_classes(module)
    if classes:
        lines.append("## Classes")
        lines.append("")
        for name, cls in classes:
            sig = format_signature(cls)
            doc = get_docstring(cls)
            lines.append(f"### `{name}{sig}`")
            lines.append("")
            if doc:
                lines.append(doc)
                lines.append("")

            # Methods
            methods = []
            for mn, meth in inspect.getmembers(cls, inspect.isfunction):
                if not mn.startswith("_"):
                    methods.append((mn, meth))
            if methods:
                lines.append("**Methods:**")
                lines.append("")
                for mn, meth in methods:
                    msig = format_signature(meth)
                    mdoc = get_docstring(meth).split("\n")[0] if get_docstring(meth) else ""
                    lines.append(f"- `{mn}{msig}` &mdash; {mdoc}")
                lines.append("")

    # Functions
    funcs = get_functions(module)
    if funcs:
        lines.append("## Functions")
        lines.append("")
        for name, fn in funcs:
            sig = format_signature(fn)
            doc = get_docstring(fn)
            lines.append(f"### `{name}{sig}`")
            lines.append("")
            if doc:
                lines.append(doc)
                lines.append("")

    doc_path.write_text("\n".join(lines), encoding="utf-8")


def generate_api_docs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    visited: Set[str] = set()

    modules_to_doc = [
        ("vdoc", vdoc),
    ]

    # Walk packages manually
    pkg_dir = Path(vdoc.__file__).resolve().parent
    for py_file in sorted(pkg_dir.rglob("*.py")):
        if py_file.name == "__init__.py":
            continue
        if "site-packages" in str(py_file):
            continue
        if "__pycache__" in str(py_file):
            continue

        rel = py_file.relative_to(pkg_dir.parent.parent if "site-packages" in str(py_file) else pkg_dir.parent)
        # Build dotted module path
        parts = list(rel.parts)
        if parts[0] == "vdoc":
            pass  # already starts with vdoc
        else:
            parts = ["vdoc"] + parts
        if py_file.name == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = py_file.stem

        mod_name = ".".join(parts)
        try:
            mod = __import__(mod_name)
            for p in mod_name.split(".")[1:]:
                mod = getattr(mod, p)
            generate_module_docs(mod, mod_name, output_dir, visited)
        except (ImportError, AttributeError) as e:
            print(f"  Skipping {mod_name}: {e}")

    # Write index
    index_lines = [
        "# VDOC API Reference",
        "",
        f"Auto-generated from source code (`vdoc` package).",
        "",
        "## Packages",
        "",
    ]
    for md_file in sorted(output_dir.glob("*.md")):
        if md_file.name != "index.md":
            name = md_file.stem
            index_lines.append(f"- [{name}]({md_file.name})")
    index_lines.append("")
    (output_dir / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    print(f"\nDocs generated in {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate VDOC API reference docs")
    parser.add_argument("--output", default="docs/api", help="Output directory")
    args = parser.parse_args()
    generate_api_docs(Path(args.output))


if __name__ == "__main__":
    main()
