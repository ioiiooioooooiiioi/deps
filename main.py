import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple

FILE_EXTENSIONS = (".ts", ".tsx", ".js", ".jsx")


def extract_imports(file_content: str) -> List[str]:
    """Extract dependencies from file content."""
    pattern = re.compile(
        r'^\s*(?!//)(?:import(?:[\s,{]+[\w*{}\s,]*?)?\sfrom\s|import\()\s*[\'"]([^\'"]+)[\'"]',
        re.MULTILINE,
    )
    return pattern.findall(file_content)


def resolve_path(import_path: str, current_file: Path, root: Path) -> Path | None:
    """Resolve import path relative to current file or src root."""
    base = current_file.parent if import_path.startswith(".") else root / "src"
    potential_paths = [
        base / import_path,
        *(base / f"{import_path}{ext}" for ext in FILE_EXTENSIONS),
        *(base / import_path / f"index{ext}" for ext in FILE_EXTENSIONS),
    ]
    for path in potential_paths:
        if path.is_file():
            return path.resolve()
    return None


def build_dependency_graph(project_root: Path) -> Dict[str, List[str]]:
    """Create a dependency graph."""
    graph = {}
    files = [
        f
        for f in project_root.rglob("*")
        if f.is_file() and f.suffix in FILE_EXTENSIONS and "node_modules" not in f.parts
    ]

    for file_path in files:
        rel_file = str(file_path.relative_to(project_root))
        imports = extract_imports(file_path.read_text("utf-8"))

        resolved_imports = []
        for imp in imports:
            imp_path = resolve_path(imp, file_path, project_root)
            if imp_path and project_root in imp_path.parents:
                resolved_imports.append(str(imp_path.relative_to(project_root)))

        graph[rel_file] = resolved_imports
    return graph


def to_mermaid(graph: Dict[str, List[str]]) -> str:
    """Convert dependency graph to Mermaid format."""

    def sanitize(s: str) -> str:
        return s.replace(".", "_").replace("/", "_").replace("-", "_")

    lines = ["graph LR"]
    for src, targets in graph.items():
        for tgt in targets:
            lines.append(f'    {sanitize(src)}["{src}"] --> {sanitize(tgt)}["{tgt}"]')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid dependency diagram.")
    parser.add_argument("project_path", type=Path, help="Path to project root")
    args = parser.parse_args()

    graph = build_dependency_graph(args.project_path)
    print(to_mermaid(graph))


if __name__ == "__main__":
    main()
