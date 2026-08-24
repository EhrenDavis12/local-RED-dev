"""
`assetgen.yaml` — cli-v1 R6-R13. Loading and validating the calling
project's config file, which every other module reads paths from.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from agf.errors import ConfigError

REQUIRED_KEYS = {"manifest", "drafts", "record"}
OPTIONAL_KEYS = {"samples", "base"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS

DEFAULT_CONFIG_FILENAME = "assetgen.yaml"


@dataclass
class Config:
    path: Path
    root: Path
    manifest: Path
    drafts: Path
    record: Path
    samples: Path | None
    base: Path | None

    @property
    def lock_path(self) -> Path:
        # R72: "<record filename>.lock", beside the record.
        return self.record.with_name(self.record.name + ".lock")


def resolve_config_path(config_arg: str | None) -> Path:
    """R6/R7: --config overrides the default `./assetgen.yaml` for one run."""
    if config_arg:
        return Path(config_arg)
    return Path(DEFAULT_CONFIG_FILENAME)


def load_config(config_arg: str | None) -> Config:
    config_path = resolve_config_path(config_arg)
    if not config_path.exists():
        raise ConfigError(
            f"config file not found: {config_path}",
            remedy=f"create {DEFAULT_CONFIG_FILENAME} or pass --config <path>",
        )

    try:
        text = config_path.read_text()
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"config file {config_path} is not valid YAML: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"config file {config_path} could not be read: {exc}") from exc

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"config file {config_path} must be a mapping of keys")

    unknown = set(data.keys()) - ALLOWED_KEYS
    if unknown:
        raise ConfigError(
            f"config file {config_path} has unknown key(s): {', '.join(sorted(unknown))}"
        )
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ConfigError(
            f"config file {config_path} is missing required key(s): {', '.join(sorted(missing))}"
        )

    # R10: every value resolves relative to the config file's own directory.
    root = config_path.resolve().parent

    def resolve(value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (root / p).resolve()

    manifest = resolve(data["manifest"])
    if not manifest.exists():
        raise ConfigError(f"declared 'manifest' path does not exist: {manifest}")

    drafts = resolve(data["drafts"])
    if not drafts.exists():
        raise ConfigError(f"declared 'drafts' path does not exist: {drafts}")

    record = resolve(data["record"])
    if not record.parent.exists():
        raise ConfigError(
            f"'record' path's parent directory does not exist: {record.parent}"
        )

    samples = None
    if "samples" in data:
        samples = resolve(data["samples"])
        if not samples.exists():
            raise ConfigError(f"declared 'samples' path does not exist: {samples}")

    base = None
    if "base" in data:
        base = resolve(data["base"])
        if not base.exists():
            raise ConfigError(f"declared 'base' path does not exist: {base}")

    # R11: a record path resolving inside drafts, at any depth, exits 2 — its
    # temp copy and the lock would otherwise sit in the sweep's own scan path.
    if record == drafts or drafts in record.parents:
        raise ConfigError(
            f"'record' path {record} resolves inside the 'drafts' area {drafts}, "
            "which is not allowed"
        )

    return Config(
        path=config_path.resolve(),
        root=root,
        manifest=manifest,
        drafts=drafts,
        record=record,
        samples=samples,
        base=base,
    )
