"""Executable dependency and purity boundaries for the CDS package."""

from __future__ import annotations

import ast
from importlib.util import resolve_name
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "cds"

LAYERS = {
    "app",
    "content",
    "domain",
    "interfaces",
    "mappers",
    "repositories",
    "rules",
    "services",
    "utils",
    "validation",
}

ALLOWED_INTERNAL_IMPORTS = {
    "domain": {"domain"},
    "validation": {"domain", "utils", "validation"},
    "services": {"domain", "services", "utils"},
    "rules": {"domain", "repositories", "rules", "utils"},
    "content": {"content", "domain"},
    "repositories": {"domain", "repositories", "utils"},
    "app": {"app", "domain", "repositories", "rules", "services", "utils", "validation"},
    "mappers": {"app", "domain", "mappers", "utils"},
    "interfaces": {"app", "domain", "interfaces", "mappers", "utils"},
    "utils": {"utils"},
}

PURE_LAYERS = {"domain", "rules", "services"}
FORBIDDEN_IO_IMPORT_ROOTS = {
    "csv",
    "ftplib",
    "http",
    "httpx",
    "io",
    "json",
    "os",
    "pathlib",
    "requests",
    "smtplib",
    "socket",
    "sqlite3",
    "sqlalchemy",
    "subprocess",
    "urllib",
    "yaml",
}


def _layer_for_path(path: Path) -> str | None:
    relative_parts = path.relative_to(SRC_ROOT).parts
    if not relative_parts:
        return None
    return relative_parts[0] if relative_parts[0] in LAYERS else None


def _module_name(path: Path) -> str:
    relative = path.relative_to(SRC_ROOT).with_suffix("")
    parts = ["cds", *relative.parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    current_module = _module_name(path)
    package = current_module if path.name == "__init__.py" else current_module.rpartition(".")[0]
    imports: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name) for alias in node.names)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level:
            relative_name = "." * node.level + (node.module or "")
            imported_module = resolve_name(relative_name, package)
        else:
            imported_module = node.module or ""

        if imported_module == "cds" and node.names:
            imports.extend(
                (node.lineno, f"cds.{alias.name}")
                for alias in node.names
                if alias.name != "*"
            )
        elif node.module is None and node.names:
            imports.extend(
                (node.lineno, f"{imported_module}.{alias.name}")
                for alias in node.names
                if alias.name != "*"
            )
        elif imported_module:
            imports.append((node.lineno, imported_module))

    return imports


def _internal_layer(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) < 2 or parts[0] != "cds":
        return None
    return parts[1] if parts[1] in LAYERS else None


def test_architecture_layer_directories_exist() -> None:
    missing = sorted(layer for layer in LAYERS if not (SRC_ROOT / layer).is_dir())
    assert not missing, f"Missing architecture layer directories: {', '.join(missing)}"


def test_internal_imports_follow_dependency_direction() -> None:
    violations: list[str] = []

    for path in sorted(SRC_ROOT.rglob("*.py")):
        source_layer = _layer_for_path(path)
        if source_layer is None:
            continue
        allowed = ALLOWED_INTERNAL_IMPORTS[source_layer]
        for line, module in _imports(path):
            target_layer = _internal_layer(module)
            if target_layer is not None and target_layer not in allowed:
                relative = path.relative_to(SRC_ROOT.parent.parent)
                violations.append(
                    f"{relative}:{line}: {source_layer} must not import "
                    f"{target_layer} via {module}"
                )

    assert not violations, "Architecture dependency violations:\n" + "\n".join(violations)


def test_pure_layers_do_not_import_io_boundaries() -> None:
    violations: list[str] = []

    for path in sorted(SRC_ROOT.rglob("*.py")):
        source_layer = _layer_for_path(path)
        if source_layer not in PURE_LAYERS:
            continue
        for line, module in _imports(path):
            if module.startswith("cds."):
                continue
            root = module.partition(".")[0]
            if root in FORBIDDEN_IO_IMPORT_ROOTS:
                relative = path.relative_to(SRC_ROOT.parent.parent)
                violations.append(
                    f"{relative}:{line}: pure {source_layer} module imports I/O boundary {module}"
                )

    assert not violations, "Pure-layer I/O import violations:\n" + "\n".join(violations)
