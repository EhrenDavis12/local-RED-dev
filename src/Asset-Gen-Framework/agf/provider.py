"""
The provider boundary — cli-v1 R75.

Every call to Replicate is made through the two functions below and nowhere
else. Nothing outside this module opens a connection to Replicate, and no
code outside it ever sees the credential except to hand it to `run` or
`upload` (R31) — and never to a model-controlled URL, such as one of the
prediction's own result files (R31/R42): those are pre-signed and need no
auth header at all.

Callers must always go through the module attribute (`provider.run(...)`),
never `from agf.provider import run`, so that a test's `monkeypatch.setattr`
on this module is actually honoured.
"""
from __future__ import annotations

import time
from pathlib import Path

import requests

_API_BASE = "https://api.replicate.com/v1"
_POLL_INTERVAL_SECONDS = 1.0

# R32 forbids a timeout on a prediction that is genuinely still running, so
# these are the only two kinds of status the poll loop distinguishes: one it
# waits on indefinitely, and everything else — including an absent status —
# which is a malformed response, never a slow one, and fails immediately.
_TERMINAL_STATUSES = {"succeeded", "failed", "canceled"}
_IN_PROGRESS_STATUSES = {"starting", "processing"}


class ProviderError(Exception):
    """Raised by `run` or `upload` on a rejected request, a failed or
    canceled prediction, or a transport failure (R33, R75)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _as_prediction(data) -> dict:
    """Every prediction envelope must be an object — a top-level list, a
    bare string, or anything else is a malformed response, not something to
    read fields off (R75)."""
    if not isinstance(data, dict):
        raise ProviderError(
            f"Replicate returned an unexpected response: expected an object, "
            f"got {type(data).__name__}"
        )
    return data


def _normalized_urls(prediction: dict) -> dict:
    """`urls`, when present, must be an object. An explicit `null` (or any
    other non-object) is a malformed shape worth failing on now, not
    something to silently paper over as if the key had simply been
    omitted — `.get("urls", {})`'s default only ever fires for a missing
    key, never an explicit null, which is exactly what let this escape as
    an AttributeError before."""
    if "urls" not in prediction:
        return {}
    urls_field = prediction["urls"]
    if not isinstance(urls_field, dict):
        raise ProviderError(
            "Replicate returned a malformed prediction response: 'urls' is "
            f"{'null' if urls_field is None else type(urls_field).__name__}, expected an object"
        )
    return urls_field


def run(model_id: str, inputs: dict, api_token: str) -> dict:
    """R75: predict. Polls until the prediction reaches a terminal state and
    fetches the result files itself, so no second path to the network is
    needed to obtain them. Returns {"version", "seed", "outputs": [bytes]}.

    Every envelope this function receives — the POST response and each poll
    — is validated defensively before anything reads a field off it: R75
    requires ProviderError, and only ProviderError, to cross this boundary,
    never a raw AttributeError/KeyError/TypeError from a malformed or
    unexpected response shape."""
    headers = {"Authorization": f"Bearer {api_token}"}

    if ":" in model_id:
        owner_name, version_hash = model_id.split(":", 1)
        create_url = f"{_API_BASE}/predictions"
        body = {"version": version_hash, "input": inputs}
    else:
        owner_name = model_id
        create_url = f"{_API_BASE}/models/{model_id}/predictions"
        body = {"input": inputs}

    prediction = _as_prediction(_post_json(create_url, body, headers))
    urls_field = _normalized_urls(prediction)

    status = prediction.get("status")
    while status not in _TERMINAL_STATUSES:
        if status not in _IN_PROGRESS_STATUSES:
            # Not a prediction taking a long time — R32's no-timeout promise
            # is about genuine progress, and this is not that: a response
            # with no recognisable status (or none at all) is a provider
            # that is not answering the question, not one still working.
            raise ProviderError(
                f"Replicate returned an unrecognised or missing prediction status: {status!r}"
            )
        get_url = urls_field.get("get")
        if not get_url:
            prediction_id = prediction.get("id")
            if not prediction_id:
                raise ProviderError(
                    "Replicate's prediction response has neither a 'urls.get' link nor "
                    "an 'id' to poll"
                )
            get_url = f"{_API_BASE}/predictions/{prediction_id}"
        time.sleep(_POLL_INTERVAL_SECONDS)
        prediction = _as_prediction(_get_json(get_url, headers))
        urls_field = _normalized_urls(prediction)
        status = prediction.get("status")

    if status != "succeeded":
        raise ProviderError(str(prediction.get("error") or f"prediction {status}"))

    version_hash = prediction.get("version") or ""
    pinned_version = f"{owner_name}:{version_hash}" if version_hash else owner_name

    # Replicate's public API does not expose a standardised "seed the model
    # picked" field on the prediction resource — there is no seed to read
    # back here beyond what the caller already declared (R50 handles that
    # case outside this boundary), so this is honestly None rather than a
    # guess at a field that may not exist for a given model.
    seed = None

    output = prediction.get("output")
    if output is None:
        urls = []
    elif isinstance(output, list):
        urls = output
    else:
        urls = [output]

    # These URLs are model-controlled, not Replicate's own API — and
    # Replicate's result files are pre-signed, so no credential is sent
    # fetching them (R31).
    outputs = [_get_bytes(url) for url in urls]

    return {"version": pinned_version, "seed": seed, "outputs": outputs}


def upload(local_path: Path, api_token: str) -> str:
    """R75: upload a referenced file to Replicate's file endpoint and return
    the URL it hands back (R42)."""
    headers = {"Authorization": f"Bearer {api_token}"}
    local_path = Path(local_path)
    try:
        with open(local_path, "rb") as fh:
            response = requests.post(
                f"{_API_BASE}/files",
                headers=headers,
                files={"content": (local_path.name, fh)},
                timeout=120,
            )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, OSError) as exc:
        raise ProviderError(f"uploading {local_path} to Replicate failed: {exc}") from exc
    except ValueError as exc:
        raise ProviderError(
            f"Replicate's file endpoint returned a response that was not valid JSON: {exc}"
        ) from exc

    url = (data.get("urls") or {}).get("get") or data.get("url")
    if not url:
        raise ProviderError(f"Replicate's file endpoint returned no URL for {local_path}")
    return url


def _post_json(url: str, body: dict, headers: dict) -> dict:
    try:
        response = requests.post(url, json=body, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ProviderError(f"request to Replicate failed: {exc}") from exc
    except ValueError as exc:
        raise ProviderError(
            f"Replicate returned a response that was not valid JSON: {exc}"
        ) from exc


def _get_json(url: str, headers: dict) -> dict:
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ProviderError(f"polling Replicate failed: {exc}") from exc
    except ValueError as exc:
        raise ProviderError(
            f"Replicate returned a response that was not valid JSON while polling: {exc}"
        ) from exc


def _get_bytes(url: str) -> bytes:
    """Fetch a result file with no Authorization header — these URLs are
    model-controlled, and Replicate's result files are pre-signed and need
    no credential (R31)."""
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ProviderError(f"fetching a result file from Replicate failed: {exc}") from exc
    return response.content
