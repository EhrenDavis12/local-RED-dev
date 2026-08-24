"""
Shared fixtures for the agf CLI test suite.

Written from `Docs/asset-gen-framework/PRDs/cli-v1.md` (cli-v1), before any
implementation exists. The provider and extraction boundaries below are no
longer this suite's own convention — R74 and R75 name and shape them
exactly this way, specifically so a test can substitute for them:

  agf.cli.main(argv: list[str]) -> int
      The whole program. Never raises: every failure is caught (R4) and
      reported as a JSON document on stdout with the matching exit code.

  agf.provider.run(model_id: str, inputs: dict, api_token: str) -> dict
      R75: the one seam through which every Replicate prediction call is
      made. Fetching the result files sits behind this boundary too — the
      autouse guard below is total. Returns {"version": "<pinned
      owner/name:hash>", "seed": int | None, "outputs": [bytes, ...]}.

  agf.provider.upload(local_path: pathlib.Path, api_token: str) -> str
      R75: the one seam through which a file is uploaded to Replicate's file
      endpoint (R42). Returns the URL the endpoint handed back.

  agf.provider.ProviderError(message: str)
      R75: raised by either provider function to signal a failed or
      canceled prediction, a rejected request, or a transport failure
      (R33) — the CLI is expected to catch this specifically and exit 6
      with `message` as the provider's own error text. Any other exception
      escaping the boundary is NOT this, and is expected to surface as
      R28's internal failure, exit 11.

  agf.frames.extract(source_path: pathlib.Path, format: str) -> list[bytes]
      R74: the one seam through which a video is read and decoded for
      `extract_frames`. Takes the resolved `source` path and the entry's
      declared `format`; returns one already-encoded frame per element, in
      video order. This is what makes the multi-file commit path
      (displace, rename, delete — R67) testable with no video and no
      decoder present.

  agf.frames.ExtractionError(message: str)
      R74: raised by extract when the source cannot be read or decoded —
      exits 12 (not 6: a local decode failure and a remote provider
      failure need different remedies). Any other exception escaping the
      boundary is not this and surfaces as exit 11.

Every test in this suite reaches the network, and reads video, exclusively
through those boundaries, and an autouse fixture below replaces all three
functions with something that raises unless a test explicitly opts in via
`fake_provider` / `fake_extraction`. No test may remove that guard. If the
real implementation calls Replicate or decodes video through some other
path, these tests cannot see it and the guard will not fire — that is a
gap the code review, not this suite, has to close.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml
from PIL import Image

import requests

import agf.cli as cli
import agf.frames as frames
import agf.provider as provider

# Captured before any fixture below monkeypatches provider.run/upload, so a
# test can call the REAL implementation directly (see
# `real_provider_fake_http`) — for defects that live inside provider.run's
# own HTTP plumbing, where swapping the whole function out (as
# `fake_provider` does) would hide the very bug being tested.
REAL_PROVIDER_RUN = provider.run
REAL_PROVIDER_UPLOAD = provider.upload


# ---------------------------------------------------------------------------
# Network guard — autouse, no test may make a real provider call.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _block_real_provider_calls(monkeypatch):
    def _blocked_run(*args, **kwargs):
        raise AssertionError(
            "agf.provider.run was called without a test stubbing it via "
            "fake_provider — no test may reach Replicate."
        )

    def _blocked_upload(*args, **kwargs):
        raise AssertionError(
            "agf.provider.upload was called without a test stubbing it via "
            "fake_provider — no test may reach Replicate."
        )

    def _blocked_extract(*args, **kwargs):
        raise AssertionError(
            "agf.frames.extract was called without a test stubbing it via "
            "fake_extraction — no test may read a real video."
        )

    monkeypatch.setattr(provider, "run", _blocked_run)
    monkeypatch.setattr(provider, "upload", _blocked_upload)
    monkeypatch.setattr(frames, "extract", _blocked_extract)


@pytest.fixture
def fake_provider(monkeypatch):
    """Install canned provider.run / provider.upload and record every call."""
    calls = {"run": [], "upload": []}

    def install(run_result=None, run_side_effect=None, upload_result="https://files.replicate.delivery/fake"):
        def _run(model_id, inputs, api_token):
            calls["run"].append(
                {"model_id": model_id, "inputs": dict(inputs), "api_token": api_token}
            )
            if run_side_effect is not None:
                return run_side_effect(model_id, inputs, api_token)
            return run_result

        def _upload(local_path, api_token):
            calls["upload"].append({"path": Path(local_path), "api_token": api_token})
            return upload_result

        monkeypatch.setattr(provider, "run", _run)
        monkeypatch.setattr(provider, "upload", _upload)
        return calls

    install.calls = calls
    return install


@pytest.fixture
def fake_extraction(monkeypatch):
    """Install a canned agf.frames.extract and record every call (R74)."""
    calls = {"extract": []}

    def install(frames_result=None, side_effect=None):
        def _extract(source_path, format):
            calls["extract"].append({"source_path": Path(source_path), "format": format})
            if side_effect is not None:
                return side_effect(source_path, format)
            return frames_result

        monkeypatch.setattr(frames, "extract", _extract)
        return calls

    install.calls = calls
    return install


# ---------------------------------------------------------------------------
# A fake HTTP layer for exercising the REAL agf.provider.run/upload against
# no network at all — for defects inside provider.run's own request-
# building, polling and error-handling, which `fake_provider` (swapping out
# the whole function) cannot see.
# ---------------------------------------------------------------------------

class FakeResponse:
    """Stands in for a `requests.Response`."""

    def __init__(self, json_data=None, content=b"", status_code=200, json_exc=None):
        self._json_data = json_data
        self.content = content
        self.status_code = status_code
        self._json_exc = json_exc

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(
                f"FakeResponse configured with status {self.status_code} but no test "
                "here exercises a transport-error path"
            )

    def json(self):
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_data


class FakeHTTP:
    """Stands in for the `requests` module as `agf.provider` sees it."""

    # provider.py's `except requests.RequestException` clauses need this
    # attribute to exist even on paths this fake never intends to exercise
    # — otherwise Python raises AttributeError evaluating the except clause
    # instead of letting whatever really happened propagate.
    RequestException = requests.RequestException

    def __init__(self):
        self.post_calls = []
        self.get_calls = []
        self._post_queue = []
        self._get_by_url = {}

    def queue_post(self, response):
        self._post_queue.append(response)

    def set_get(self, url, response_or_factory):
        """`response_or_factory` is either a FakeResponse, reused for every
        call to `url`, or a callable(call_number) -> FakeResponse for
        simulating a sequence (e.g. a poll loop)."""
        self._get_by_url[url] = response_or_factory

    def post(self, url, json=None, headers=None, timeout=None, **kwargs):
        self.post_calls.append({"url": url, "json": json, "headers": dict(headers or {})})
        if not self._post_queue:
            raise AssertionError(f"unexpected POST to {url} — no response was queued for it")
        return self._post_queue.pop(0)

    def get(self, url, headers=None, timeout=None, **kwargs):
        self.get_calls.append({"url": url, "headers": dict(headers or {})})
        target = self._get_by_url.get(url)
        if target is None:
            raise AssertionError(f"unexpected GET to {url} — no response was configured for it")
        if callable(target):
            return target(len(self.get_calls))
        return target


class _InstantTime:
    """Stands in for the `time` module so a poll loop's `time.sleep` never
    actually waits — needed to safely exercise defect 8 (a poll loop that
    does not terminate) without the test itself hanging."""

    @staticmethod
    def sleep(seconds):
        pass


@pytest.fixture
def real_provider_fake_http(monkeypatch):
    """
    Restores the REAL agf.provider.run/upload (undoing the autouse network
    guard for this one test — see REAL_PROVIDER_RUN above) and replaces the
    `requests` module and `time` module *as agf.provider itself sees them*
    with fakes, so the real request-building, polling and error-handling
    logic in provider.py runs for real, against no network and no actual
    waiting. Returns the FakeHTTP to configure responses on and inspect
    calls from.
    """
    fake_http = FakeHTTP()
    monkeypatch.setattr(provider, "run", REAL_PROVIDER_RUN)
    monkeypatch.setattr(provider, "upload", REAL_PROVIDER_UPLOAD)
    monkeypatch.setattr(provider, "requests", fake_http)
    monkeypatch.setattr(provider, "time", _InstantTime())
    return fake_http


# ---------------------------------------------------------------------------
# The record's closed key set — R47 names exactly these sixteen keys, every
# one present on every entry the framework writes, whatever its type and
# operation.
# ---------------------------------------------------------------------------

RECORD_ENTRY_KEYS = frozenset(
    {
        "operation",
        "type",
        "model",
        "model_version",
        "prompt",
        "prompt_key",
        "seed",
        "inputs",
        "input_files",
        "output",
        "format",
        "frame_count",
        "frame_size",
        "layout",
        "frames",
        "source",
    }
)


def full_record_entry(**overrides):
    """A record entry with all sixteen R47 keys, defaulting to null, so a
    hand-written fixture never silently falls out of shape when the schema
    changes."""
    entry = {key: None for key in RECORD_ENTRY_KEYS}
    entry.update(overrides)
    return entry


CHECKS_KEYS = frozenset({"format", "layout", "frame_size", "frame_count", "output_count"})


def assert_checks_list_shape(checks_list):
    """R71/R5: error.checks is always a list, one {path, checks} element per
    file the entry produced, each checks object carrying the full five-key
    set — never trimmed to the failing one."""
    assert isinstance(checks_list, list) and len(checks_list) >= 1
    for element in checks_list:
        assert set(element.keys()) == {"path", "checks"}
        assert set(element["checks"].keys()) == CHECKS_KEYS
    return checks_list


# ---------------------------------------------------------------------------
# CLI invocation helper
# ---------------------------------------------------------------------------

@pytest.fixture
def run_cli(capsys):
    """Invoke agf.cli.main in-process and capture (exit_code, stdout, stderr)."""

    def _run(args):
        exit_code = cli.main(list(args))
        captured = capsys.readouterr()
        return exit_code, captured.out, captured.err

    return _run


def parse_single_json_document(stdout: str) -> dict:
    """
    Assert stdout holds exactly one JSON document and nothing else (R4), and
    return the parsed document.
    """
    text = stdout.strip()
    assert text, "stdout was empty; every command must print one JSON document"
    decoder = json.JSONDecoder()
    doc, end = decoder.raw_decode(text)
    trailing = text[end:].strip()
    assert trailing == "", (
        f"stdout held more than one JSON document; trailing content: {trailing!r}"
    )
    return doc


# ---------------------------------------------------------------------------
# Calling-project fixture: assetgen.yaml + manifest.yaml + drafts/samples/base
# ---------------------------------------------------------------------------

@dataclass
class Project:
    root: Path
    config_path: Path
    manifest_path: Path
    drafts: Path
    samples: Path
    base: Path
    record_path: Path

    def config_args(self):
        return ["--config", str(self.config_path)]


@pytest.fixture
def project(tmp_path) -> Project:
    root = tmp_path / "calling_project"
    root.mkdir()
    drafts = root / "drafts"
    drafts.mkdir()
    samples = root / "samples"
    samples.mkdir()
    base = root / "base"
    base.mkdir()
    manifest_path = root / "manifest.yaml"
    manifest_path.write_text("[]\n")
    record_path = root / "record.json"
    config_path = root / "assetgen.yaml"

    p = Project(root, config_path, manifest_path, drafts, samples, base, record_path)
    write_config(p)
    # A stand-in video file so extract_frames_entry()'s default `source:
    # samples:video.mp4` resolves (R43 requires the referenced file to
    # exist) without every manifest-shape test having to create one itself.
    # Its bytes are never read — no test drives extract_frames execution.
    (samples / "video.mp4").write_bytes(b"not a real video, just needs to exist")
    return p


def write_config(p: Project, **overrides):
    """(Re)write assetgen.yaml. Pass a key=None to omit that key entirely."""
    data = {
        "manifest": "manifest.yaml",
        "drafts": "drafts",
        "record": "record.json",
        "samples": "samples",
        "base": "base",
    }
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    p.config_path.write_text(yaml.safe_dump(data, sort_keys=False))


def write_raw_config(p: Project, text: str):
    p.config_path.write_text(text)


def write_manifest(p: Project, entries: list[dict]):
    p.manifest_path.write_text(yaml.safe_dump(entries, sort_keys=False))


def write_raw_manifest(p: Project, text: str):
    p.manifest_path.write_text(text)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def make_png(path: Path, size=(10, 10), color=(255, 0, 0, 255)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, color).save(path, format="PNG")


def png_bytes(size=(10, 10), color=(255, 0, 0, 255)) -> bytes:
    import io

    buf = io.BytesIO()
    Image.new("RGBA", size, color).save(buf, format="PNG")
    return buf.getvalue()


def truncated_png_bytes(size=(10, 10), color=(200, 50, 100, 128)) -> bytes:
    """
    A PNG cut off partway through its pixel data — not merely a file with a
    wrong suffix. PIL's `Image.open` reads only the header, so this still
    reports the correct `.size`, but decoding pixel data (`.load()` /
    `.convert()`) raises. Used to reach the class of bug where a check that
    only inspects the header (frame_size) passes while a later step that
    actually decodes the frame does not.

    Self-checks at construction time — if a future Pillow version changes
    how much of the file `Image.open` needs before it will decode, this
    raises a clear fixture-setup error here rather than silently exercising
    a different, unintended code path in the test that uses it.
    """
    import io

    full = png_bytes(size=size, color=color)
    truncated = full[: len(full) // 2]

    with Image.open(io.BytesIO(truncated)) as probe:
        assert probe.size == size, "fixture bug: truncation broke the header, not just the pixel data"
        try:
            probe.load()
        except Exception:
            pass
        else:
            raise AssertionError("fixture bug: truncated PNG decoded successfully — truncate further")
    return truncated


# ---------------------------------------------------------------------------
# Manifest entry builders — minimal legal entries of each shape.
# ---------------------------------------------------------------------------

def image_model_entry(name="img1", output="img1.png", model=None, prompt="a cat", **extra):
    entry = {"name": name, "type": "image", "output": output, "format": "png"}
    if model is not None:
        entry["model"] = model
    if prompt is not None:
        entry["prompt"] = prompt
    entry.update(extra)
    return entry


def sheet_assemble_entry(
    name="sheet1",
    output="sheet1.png",
    frames=None,
    frame_count=4,
    frame_size=(10, 10),
    layout=None,
    **extra,
):
    if frames is None:
        frames = [f"samples:frames/f{i}.png" for i in range(frame_count)]
    if layout is None:
        layout = {"columns": 2, "rows": 2}
    entry = {
        "name": name,
        "type": "sprite_sheet",
        "operation": "assemble_sheet",
        "output": output,
        "format": "png",
        "frames": frames,
        "frame_count": frame_count,
        "frame_size": list(frame_size),
        "layout": layout,
    }
    entry.update(extra)
    return entry


def sheet_model_entry(
    name="sheet_m",
    output="sheet_m.png",
    model="acme/sheetmaker",
    frame_count=4,
    frame_size=(10, 10),
    layout=None,
    prompt="walk cycle",
    **extra,
):
    if layout is None:
        layout = {"columns": 2, "rows": 2}
    entry = {
        "name": name,
        "type": "sprite_sheet",
        "model": model,
        "output": output,
        "format": "png",
        "prompt": prompt,
        "frame_count": frame_count,
        "frame_size": list(frame_size),
        "layout": layout,
    }
    entry.update(extra)
    return entry


def extract_frames_entry(name="frames1", output="frames1/walk_{n:03d}.png", frame_count=None, **extra):
    entry = {
        "name": name,
        "type": "image",
        "operation": "extract_frames",
        "output": output,
        "format": "png",
        "source": "samples:video.mp4",
    }
    if frame_count is not None:
        entry["frame_count"] = frame_count
    entry.update(extra)
    return entry
