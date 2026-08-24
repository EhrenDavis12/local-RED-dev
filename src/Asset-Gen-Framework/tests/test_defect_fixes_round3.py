"""
Regression tests from a second correctness re-review, after the round-2
defect fixes landed (`tests/test_defect_fixes.py`). One of those fixes
introduced a worse bug (item 1); the rest are gaps the re-review found
elsewhere. Written from the PRD (and, for items 2 and 4, from the exact
rule the coordinator handed down for a PRD update in flight) — never from
what `agf/*.py` currently does.

Every test here is expected to FAIL against the code as it stands and PASS
once each item is fixed.
"""
from __future__ import annotations

import pytest

import agf.provider as provider_module
from conftest import (
    REAL_PROVIDER_RUN,
    FakeResponse,
    assert_checks_list_shape,
    extract_frames_entry,
    image_model_entry,
    make_png,
    parse_single_json_document,
    sheet_assemble_entry,
    sheet_model_entry,
    truncated_png_bytes,
    write_manifest,
)


# ---------------------------------------------------------------------------
# 1. Regression from the defect-9 fix: a truncated frame silently commits a
#    transparent cell instead of failing.
# ---------------------------------------------------------------------------

def test_regression1_truncated_frame_fails_frame_size_not_silently_transparent(project, run_cli):
    """
    The defect-9 fix wrapped `_run_assemble_sheet`'s paste loop in
    `except Exception: continue`. `check_frame_sizes` only calls
    `Image.open(path)` and reads `.size` — PIL reads just the header for
    that, so a PNG truncated after its header but before its pixel data
    reports the *correct* size and passes `frame_size`. The paste loop then
    fails to decode it and the guard silently swallows that, leaving a
    fully transparent cell where a real frame should be, and the run
    exits 0 with a committed sheet and a written record.

    R61 requires a frame the framework cannot read to be a `frame_size`
    failure, exit 7, nothing committed — truncated, not merely a file with
    the wrong suffix, which the existing (already-passing) round-2 test
    already covers and would not catch this regression.
    """
    frames_dir = project.samples / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    make_png(frames_dir / "f0.png", size=(10, 10))
    (frames_dir / "f1.png").write_bytes(truncated_png_bytes(size=(10, 10)))
    make_png(frames_dir / "f2.png", size=(10, 10))
    make_png(frames_dir / "f3.png", size=(10, 10))

    entry = sheet_assemble_entry(
        name="sheet1", frames=[f"samples:frames/f{i}.png" for i in range(4)]
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)

    assert code == 7, doc
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    assert checks_list[0]["checks"]["frame_size"] == "fail"
    assert not (project.drafts / "sheet1.png").exists()
    assert not project.record_path.exists()


# ---------------------------------------------------------------------------
# 2. A frame-number format spec that never produces digits defeats R18's
#    collision check.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_template",
    [
        "frames/f_{n:.2f}.png",
        "frames/f_{n:s}.png",
        "frames/f_{n:c}.png",
        "frames/f_{n:/>5}.png",
        "frames/f_{n:9999999999d}.png",
        "frames/f_{n:5d}.png",
        "frames/f_{n:3d}.png",
    ],
    ids=[
        "float-spec",
        "string-spec",
        "char-spec",
        "fill-align-no-digits",
        "absurd-width",
        "space-padded-width-5",
        "space-padded-width-3",
    ],
)
def test_regression2_non_digit_format_spec_exits_3_and_never_extracts(project, run_cli, bad_template):
    """
    A placeholder's format spec must produce decimal digits — a plain
    placeholder, or an integer format with an optional *zero*-padded width
    — and anything else must be rejected at manifest validation, exit 3,
    before extraction. `{n:.2f}` produces `f_1.00.png`, which R18's
    digit-matching regex cannot see at all: a second `generate` would
    replace the whole frame directory with no refusal, and `list` would
    report `draft_exists: false` while the files sit right there on disk.
    The other forms here don't even produce a valid basename and today
    decode the entire video before failing to format it.

    `{n:5d}` and `{n:3d}` are the same false negative as `{n:.2f}`, not a
    crash: an integer width with no leading zero *space*-pads —
    `"{:5d}".format(7)` is `'    7'` — so it produces `f_    7.png`, which
    R18's `\\d+` collision matcher cannot see either. R63 names a
    space-padded width such as `{n:3d}` explicitly among the rejected forms.
    """
    entry = extract_frames_entry(name="f1", output=bad_template)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


def test_regression2_plain_and_zero_padded_digit_specs_remain_legal(project, run_cli):
    """The positive case, so the new validation doesn't overreach: a bare
    `{n}`, a plain `{n:d}`, and an integer format with a *zero*-padded
    width are exactly what R18's existing collision matching already
    handles — an unpadded or space-padded width is not among them (see the
    parametrized case above)."""
    for template in [
        "frames/f_{n}.png",
        "frames/f_{n:d}.png",
        "frames/f_{n:03d}.png",
        "frames/f_{n:05d}.png",
    ]:
        entry = extract_frames_entry(name="f1", output=template)
        write_manifest(project, [entry])
        code, out, _ = run_cli(["list"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 0, (template, doc)


# ---------------------------------------------------------------------------
# 3. Malformed provider envelopes still escape the boundary as something
#    other than ProviderError.
# ---------------------------------------------------------------------------

def test_regression3_null_urls_is_a_provider_error(real_provider_fake_http):
    """`prediction.get("urls", {})` only supplies the {} default when the
    key is *missing* — an explicit `"urls": null` still returns None, and
    `.get("get")` on it crashes. R75 requires ProviderError, never a raw
    AttributeError, to be what crosses the boundary."""
    real_provider_fake_http.queue_post(
        FakeResponse(
            json_data={
                "id": "pred1", "status": "succeeded", "version": "abc",
                "output": "https://delivery.replicate.com/out.png", "urls": None,
            }
        )
    )
    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")


def test_regression3_top_level_list_response_is_a_provider_error(real_provider_fake_http):
    """A response whose JSON body is a list, not an object — `prediction`
    ends up a `list`, and `.get(...)` on it crashes."""
    real_provider_fake_http.queue_post(FakeResponse(json_data=[1, 2, 3]))
    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")


def test_regression3_response_with_no_id_is_a_provider_error(real_provider_fake_http):
    """No `urls.get` and no `id` to fall back to — `prediction['id']`
    raises KeyError building the polling URL."""
    real_provider_fake_http.queue_post(
        FakeResponse(json_data={"status": "processing", "urls": {}})
    )
    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")


def test_regression3_poll_returning_a_bare_string_is_a_provider_error(real_provider_fake_http):
    """The prediction resource itself, once polled, is a bare string —
    `prediction.get("status")` crashes on it."""
    http = real_provider_fake_http
    http.queue_post(
        FakeResponse(
            json_data={
                "id": "pred1", "status": "starting",
                "urls": {"get": "https://api.replicate.com/v1/predictions/pred1"},
            }
        )
    )
    http.set_get("https://api.replicate.com/v1/predictions/pred1", FakeResponse(json_data="pong"))
    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")


def test_regression_present_but_unrecognised_poll_status_fails_immediately(real_provider_fake_http):
    """
    Coverage gap: only an *absent* status is exercised elsewhere. A status
    that is present but not one of the recognised terminal or in-progress
    values — "queued" is Replicate's own name for a real, if early, state
    this framework simply doesn't recognise — must fail the same way an
    absent one does: immediately, as a provider failure, never waited on.
    The branch's whole job is telling "not answering" from "still working",
    and a value present-but-wrong is exactly as much "not answering" as one
    that is missing.
    """
    http = real_provider_fake_http
    http.queue_post(
        FakeResponse(
            json_data={
                "id": "pred1", "status": "queued",
                "urls": {"get": "https://api.replicate.com/v1/predictions/pred1"},
            }
        )
    )
    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")
    # Failed on the very first response — never entered the poll loop at all.
    assert http.get_calls == []


# ---------------------------------------------------------------------------
# 4. Geometry is type-checked but not range-checked.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "frame_size",
    [[0, 0], [-32, 32], [32, -32], [0, 32]],
    ids=["zero-both", "negative-width", "negative-height", "zero-width"],
)
def test_regression4_non_positive_frame_size_exits_3_at_validation(project, run_cli, frame_size):
    entry = {
        "name": "sh1", "type": "sprite_sheet", "operation": "assemble_sheet",
        "output": "sh1.png", "format": "png",
        "frames": ["samples:frames/f0.png"], "frame_count": 1,
        "frame_size": frame_size,
        "layout": {"columns": 1, "rows": 1},
    }
    make_png(project.samples / "frames" / "f0.png")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


@pytest.mark.parametrize(
    "layout,frame_count",
    [
        ({"columns": 0, "rows": 5}, 0),
        ({"columns": 5, "rows": 0}, 0),
        ({"columns": -2, "rows": -3}, 1),
    ],
    ids=["zero-columns", "zero-rows", "both-negative"],
)
def test_regression4_non_positive_layout_exits_3_at_validation(project, run_cli, layout, frame_count):
    """
    A model-operation sprite_sheet entry, so there is no `frames` list to
    coincidentally trip an unrelated validation rule — isolating this to
    the layout-positivity gap alone. `frame_count` is chosen per case so
    the pre-existing `columns * rows < frame_count` arithmetic check (a
    different, already-enforced rule) doesn't happen to reject it first
    and mask the gap. A single negative dimension paired with a *positive*
    partner is not tested in isolation for the same reason: since
    `frame_count` can never be negative, that combination's product is
    always negative and so is always already caught by that pre-existing
    check — there is no way to reach execution with it today to
    demonstrate this particular gap.
    """
    entry = {
        "name": "sh1", "type": "sprite_sheet", "operation": "model", "model": "acme/x",
        "output": "sh1.png", "format": "png",
        "frame_count": frame_count, "frame_size": [10, 10],
        "layout": layout,
    }
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


def test_regression4_bad_geometry_never_reaches_image_construction(project, run_cli, monkeypatch):
    """The consequence that matters: a range-invalid geometry value must
    not spend a provider call before failing. The autouse network guard
    proves it never does."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(name="sh1", frame_size=[-10, -10])
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


@pytest.mark.parametrize("frame_count", [0, -1, -5], ids=["zero", "negative-one", "negative-five"])
def test_regression_extract_frames_frame_count_must_be_positive(project, run_cli, frame_count):
    """
    Coverage gap: R44's positivity rule is exercised only through the
    sprite-sheet geometry fields. `extract_frames`' own `frame_count` is
    the same rule applied to a different field — "not sheet geometry, but
    a negative or zero count is exactly as nonsensical for a video's frame
    yield" — and nothing pinned that it actually holds there too.
    """
    entry = extract_frames_entry(name="f1", output="frames/w_{n:03d}.png", frame_count=frame_count)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


# ---------------------------------------------------------------------------
# 5. File-vs-file containment is not checked, only file-vs-file equality.
# ---------------------------------------------------------------------------

def test_regression5_single_file_output_nested_under_another_single_files_path_is_rejected(project, run_cli):
    """
    R28's exit-3 row already promises an output that "collides with,
    contains or sits inside another entry's". Two entries' claimed
    directories are checked against each other, and a single file is
    checked against a claimed *directory* — but two ordinary (non-
    extract_frames) entries where one's `output` sits inside the other's
    `output`, treating the first as a directory component, are never
    compared: `a.png` and `a.png/b.png` both validate today, and the
    second only fails once it actually tries to commit.
    """
    entries = [
        image_model_entry(name="a", model="acme/x", output="a.png"),
        image_model_entry(name="b", model="acme/y", output="a.png/b.png"),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


def test_regression5_file_blocking_an_intermediate_directory_exits_10(
    project, run_cli, fake_provider, monkeypatch
):
    """
    A manifest that is entirely valid on its own: nothing here is a
    manifest-time defect. `execute_entry` creates any missing intermediate
    directory an entry's `output` implies (R12); if a *plain file* already
    occupies that path — left there by something else entirely, and not a
    situation any validation rule can see in advance — `mkdir` fails. R12
    now gives this a stated outcome, and R28's row 10 was retitled from
    "Commit" to "Destination" to cover both routes into it: a commit
    blocked at the destination (R67), and a plain file blocking an
    intermediate directory the destination needs. One code for both,
    because an agent's remedy is identical either way: something is in the
    way, clear it.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    (project.drafts / "sub").write_bytes(b"a plain file, not a directory")
    entry = image_model_entry(name="e1", model="acme/gen", output="sub/e1.png")
    write_manifest(project, [entry])
    from conftest import png_bytes

    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})

    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 10, doc
    message = doc["error"]["message"]
    blocked_path = str(project.drafts / "sub")
    assert blocked_path in message, f"the blocked path is not named in: {message!r}"
    assert "directory" in message.lower(), f"what is in the way is not named in: {message!r}"


# ---------------------------------------------------------------------------
# 6. R61's unreadable-frame message drops the declared frame_size.
# ---------------------------------------------------------------------------

def test_regression6_unreadable_frame_message_still_names_the_declared_frame_size(project, run_cli):
    """
    `check_layout` names the declared dimensions even when the sheet
    itself can't be read ("declared layout requires WxH pixels; the sheet
    image could not be read"). `check_frame_sizes`' matching branch drops
    it entirely — "frame f1.png could not be read as an image" never says
    what `frame_size` was declared. The actual size genuinely doesn't
    exist in this case; the declared one does, and R61 requires both.
    """
    frames_dir = project.samples / "frames"
    make_png(frames_dir / "f0.png", size=(10, 10))
    (frames_dir / "f1.png").write_bytes(b"not an image, just named like one")
    make_png(frames_dir / "f2.png", size=(10, 10))
    make_png(frames_dir / "f3.png", size=(10, 10))
    entry = sheet_assemble_entry(
        name="sheet1", frames=[f"samples:frames/f{i}.png" for i in range(4)], frame_size=(10, 10)
    )
    write_manifest(project, [entry])

    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7, doc
    message = doc["error"]["message"]
    assert "f1.png" in message, f"offending frame not named in: {message!r}"
    assert "10" in message, f"declared frame_size not named in: {message!r}"


# ---------------------------------------------------------------------------
# Coverage gap: check_layout's unreadable-sheet branch — the exact twin of
# the frame_size unreadable branch broken this round (regression 1) and
# fixed for its message this round (regression 6) — had no test of its own.
# ---------------------------------------------------------------------------

def test_regression_check_layout_unreadable_sheet_names_declared_dimensions(
    project, run_cli, fake_provider, monkeypatch
):
    """
    A model returns bytes that cannot be opened as an image at all — not
    merely the wrong size. R57 requires this to fail cleanly (exit 7,
    `layout: "fail"`), and `check_layout` already names the declared
    dimensions in this branch ("declared layout requires WxH pixels; the
    sheet image could not be read"); nothing pinned that either half of
    that actually holds.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(
        name="sh1", output="sh1.png", frame_count=4, frame_size=(10, 10),
        layout={"columns": 2, "rows": 2},
    )
    write_manifest(project, [entry])
    # Starts with a real PNG signature (so the *format* check passes,
    # isolating this to the layout check alone) but is not a decodable
    # image at all — Image.open() itself raises, not merely .load().
    undecodable_sheet = b"\x89PNG\r\n\x1a\n" + b"not a real png structure at all, just noise"
    fake_provider(
        run_result={"version": "acme/sheetmaker:v1", "seed": None, "outputs": [undecodable_sheet]}
    )

    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7, doc
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    assert checks_list[0]["checks"]["layout"] == "fail"
    message = doc["error"]["message"]
    assert "20" in message, f"declared dimensions not named in: {message!r}"
