import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple


def get_typescript_dependencies(file_path: Path) -> List[str]:
    """Extracts import dependencies from a TypeScript/JavaScript file."""
    dependencies = []
    try:
        content = file_path.read_text(encoding="utf-8")

        for match in re.findall(
            r'^\s*(?!//)(?:import(?:[\s,{]+[\w*{}, ]+[\s,}]*)?[\s]+from[\s]+|(?:import\())[\'"]([^\'"]+)[\'"]',
            content,
            re.MULTILINE,
        ):
            dependencies.append(match)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return dependencies


def is_allowed(file_path: Path, file_extensions: Tuple[str, ...]) -> bool:
    """Checks if a file should be included in the dependency graph."""
    if any(part == "node_modules" for part in file_path.parts):
        return False
    if file_path.suffix not in file_extensions:
        return False
    return True


def build_dependency_graph(
    project_path: str,
    file_extensions: Tuple[str, ...],
) -> Dict[str, List[str]]:
    """Builds a dependency graph for a TypeScript/JavaScript project."""
    graph = {}
    project_path_obj = Path(project_path)
    src_path_obj = project_path_obj / "src"  # @todo: make it configurable

    for file_path in project_path_obj.rglob("*"):
        if file_path.is_file() and is_allowed(file_path, file_extensions):
            relative_file_path = str(file_path.relative_to(project_path_obj))
            graph[relative_file_path] = []

            dependencies = get_typescript_dependencies(file_path)

            for dep in dependencies:
                if dep.startswith("."):
                    absolute_dep_path = (file_path.parent / dep).resolve()
                    found_dep_path = find_actual_file(
                        absolute_dep_path, file_extensions
                    )
                    if found_dep_path:
                        relative_dep_path = str(
                            found_dep_path.relative_to(project_path_obj)
                        )
                        graph[relative_file_path].append(relative_dep_path)

                # @todo: read from vite/ts config
                elif dep.startswith("@/"):
                    absolute_dep_path = (src_path_obj / dep[2:]).resolve()
                    found_dep_path = find_actual_file(
                        absolute_dep_path, file_extensions
                    )
                    if found_dep_path:
                        relative_dep_path = str(
                            found_dep_path.relative_to(project_path_obj)
                        )
                        graph[relative_file_path].append(relative_dep_path)

    return graph


def find_actual_file(base_path: Path, extensions: Tuple[str, ...]) -> Path | None:
    """Resolves import paths, handling missing extensions and directory imports."""
    if base_path.exists():
        if base_path.is_file():
            return base_path
        else:
            for ext in extensions:
                index_file_path = base_path / f"index{ext}"
                if index_file_path.is_file():
                    return index_file_path

    for ext in extensions:
        file_path = Path(str(base_path) + ext)
        if file_path.is_file():
            return file_path
    return None


def generate_mermaid(graph: Dict[str, List[str]]) -> str:
    """Generates a Mermaid diagram from a dependency graph."""
    mermaid_code = "graph LR\n"
    for file, dependencies in graph.items():
        file_node = file.replace(".", "_").replace("/", "_").replace("-", "_")
        for dep in dependencies:
            dep_node = dep.replace(".", "_").replace("/", "_").replace("-", "_")
            mermaid_code += f'    {file_node}["{file}"] --> {dep_node}["{dep}"]\n'
    return mermaid_code


def main():
    """Generates a Mermaid dependency diagram for a TypeScript/JavaScript project."""
    parser = argparse.ArgumentParser(
        description="Generate a Mermaid dependency diagram for a TypeScript/JavaScript project."
    )
    parser.add_argument(
        "project_path", type=Path, help="The path to the project root directory."
    )
    args = parser.parse_args()

    project_path: Path = args.project_path
    file_extensions = (".ts", ".tsx", ".js", ".jsx")

    graph = build_dependency_graph(str(project_path), file_extensions)
    mermaid = generate_mermaid(graph)
    print(mermaid)


if __name__ == "__main__":
    main()
