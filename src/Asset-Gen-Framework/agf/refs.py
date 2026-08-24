"""
File references — cli-v1 R42/R43. `<root>:<relative path>`, where `<root>`
is `samples`, `base` or `drafts`.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath

from agf.config import Config
from agf.errors import ManifestError

RESERVED_PREFIXES = (".agf-tmp-", ".agf-old-")


def _has_reserved_component(rel: str) -> bool:
    return any(
        part.startswith(RESERVED_PREFIXES) for part in PurePosixPath(rel).parts
    )


def resolve_reference(config: Config, ref: str, context: str) -> Path:
    """Resolve a `<root>:<relative path>` reference against the config,
    raising ManifestError (exit 3) per R43 if the root is undeclared or the
    file does not exist."""
    if not isinstance(ref, str) or ":" not in ref:
        raise ManifestError(f"{context}: invalid file reference {ref!r}; expected '<root>:<path>'")

    root_name, rel = ref.split(":", 1)
    roots = {"samples": config.samples, "base": config.base, "drafts": config.drafts}
    if root_name not in roots:
        raise ManifestError(f"{context}: unknown root {root_name!r} in reference {ref!r}")

    root_path = roots[root_name]
    if root_path is None:
        raise ManifestError(
            f"{context}: reference {ref!r} uses root {root_name!r}, "
            f"which is not declared in the config"
        )

    if _has_reserved_component(rel):
        raise ManifestError(
            f"{context}: reference {ref!r} touches a path reserved by the framework"
        )

    resolved = (root_path / rel).resolve()
    if not resolved.exists():
        raise ManifestError(f"{context}: referenced file {rel!r} does not exist ({resolved})")
    return resolved
