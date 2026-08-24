"""
Regression tests for defects found by a correctness review of the shipped
implementation (`agf/*.py`) against cli-v1. Written from the PRD, using the
review's findings only to know *where* to build a fixture that reaches the
bug — never to copy what the code currently does as the expected value.

Every test here is expected to FAIL against the code as it stands and PASS
once each defect is fixed; that is the point of writing them before the fix.
"""
from __future__ import annotations

import json

import pytest
from PIL import Image

import agf.provider as provider_module
from conftest import (
    REAL_PROVIDER_RUN,
    FakeResponse,
    assert_checks_list_shape,
    extract_frames_entry,
    image_model_entry,
    make_png,
    parse_single_json_document,
    png_bytes,
    sheet_assemble_entry,
    sheet_model_entry,
    write_manifest,
)


# ---------------------------------------------------------------------------
# 1. Alpha corrupted when frames are pasted into an assembled sheet.
# ---------------------------------------------------------------------------

def test_defect1_partial_alpha_survives_assembly_exactly(project, run_cli):
    """
    `_run_assemble_sheet` (agf/execute.py) pastes each frame using the frame
    itself as the paste mask, which composites rather than copies: a source
    pixel (255,0,0,128) lands in the sheet as (128,0,0,64) — colour
    premultiplied, alpha squared. It is exact only for alpha 0 or 255,
    which is why every other test's frames (built at alpha=255) never
    caught it. The committed sheet's pixels must equal the source frames'
    pixels exactly, for genuinely partial alpha.
    """
    size = (4, 4)
    colors = [
        (255, 0, 0, 128),  # the case the bug corrupts
        (0, 255, 0, 64),
        (0, 0, 255, 200),
        (10, 20, 30, 1),  # nearly transparent, non-zero
    ]
    frames_dir = project.samples / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for i, color in enumerate(colors):
        Image.new("RGBA", size, color).save(frames_dir / f"f{i}.png", format="PNG")

    entry = sheet_assemble_entry(
        name="sheet1",
        output="sheet1.png",
        frames=[f"samples:frames/f{i}.png" for i in range(4)],
        frame_count=4,
        frame_size=size,
        layout={"columns": 2, "rows": 2},
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0, doc

    with Image.open(project.drafts / "sheet1.png") as sheet:
        sheet = sheet.convert("RGBA")
        for i, color in enumerate(colors):
            col, row = i % 2, i // 2
            pixel = sheet.getpixel((col * size[0], row * size[1]))
            assert pixel == color, (
                f"frame {i}: source pixel {color} became {pixel} in the "
                "committed sheet — looks like the alpha-premultiply bug"
            )


# ---------------------------------------------------------------------------
# 2. Manifest geometry is never type-checked.
# ---------------------------------------------------------------------------

def test_defect2_non_list_frame_size_exits_3_at_validation(project, run_cli):
    """`agf list` never executes anything — if this were correctly a
    manifest-validation defect, fixing `_validate_geometry` alone (no
    change to execute.py) makes this exit 3 instead of silently accepting
    it. The referenced frame file is real and present so the only thing
    wrong with this entry is the malformed `frame_size` — otherwise R43's
    missing-file check would exit 3 for an unrelated reason and this test
    would pass today for the wrong one."""
    make_png(project.samples / "frames" / "f0.png")
    entry = {
        "name": "sh1", "type": "sprite_sheet", "operation": "assemble_sheet",
        "output": "sh1.png", "format": "png",
        "frames": ["samples:frames/f0.png"], "frame_count": 1,
        "frame_size": 64,  # not a [width, height] list at all
        "layout": {"columns": 1, "rows": 1},
    }
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


@pytest.mark.parametrize(
    "bad_frame_size",
    [64, [64], [64, "eighty"], [64, 64, 64]],
    ids=["not-a-list", "one-element", "non-int-element", "three-elements"],
)
def test_defect2_malformed_frame_size_shapes_all_exit_3(project, run_cli, bad_frame_size):
    make_png(project.samples / "frames" / "f0.png")
    entry = {
        "name": "sh1", "type": "sprite_sheet", "operation": "assemble_sheet",
        "output": "sh1.png", "format": "png",
        "frames": ["samples:frames/f0.png"], "frame_count": 1,
        "frame_size": bad_frame_size,
        "layout": {"columns": 1, "rows": 1},
    }
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


@pytest.mark.parametrize(
    "bad_layout",
    [{"columns": "two", "rows": 2}, {"columns": 2, "rows": "two"}, {"columns": 2.5, "rows": 2}],
    ids=["columns-not-int", "rows-not-int", "columns-float"],
)
def test_defect2_non_int_layout_fields_exit_3(project, run_cli, bad_layout):
    make_png(project.samples / "frames" / "f0.png")
    entry = {
        "name": "sh1", "type": "sprite_sheet", "operation": "assemble_sheet",
        "output": "sh1.png", "format": "png",
        "frames": ["samples:frames/f0.png"], "frame_count": 1,
        "frame_size": [10, 10],
        "layout": bad_layout,
    }
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


def test_defect2_bad_frame_size_never_reaches_the_provider(project, run_cli, monkeypatch):
    """The consequence that matters most: a bad geometry value must not
    spend a real provider call before failing. The default autouse network
    guard (conftest.py) proves `provider.run` was never reached — if it
    had been, this would see exit 11 from the guard's AssertionError, not 3."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(name="sh1")
    entry["frame_size"] = 64  # not a [width, height] list
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


# ---------------------------------------------------------------------------
# 3. Ctrl-C escapes and leaves debris.
# ---------------------------------------------------------------------------

def test_defect3_keyboard_interrupt_is_reported_not_left_to_escape(
    project, run_cli, fake_provider, monkeypatch
):
    """
    `except Exception` in agf/cli.py (and in execute.py's own cleanup
    try/except) does not catch KeyboardInterrupt, since it is a
    BaseException, not an Exception. R4 requires one JSON document on
    stdout and R28's internal code (11) on any unanticipated failure; R68
    names an interrupt directly among the cases that must remove staging
    and then its marker.

    This is deliberately wrapped in try/except in the test itself, never in
    pytest.raises: a raw KeyboardInterrupt escaping the test function is
    treated by pytest as an actual user interrupt and aborts the whole
    session rather than just failing this test.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen")
    write_manifest(project, [entry])
    fake_provider(run_side_effect=lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()))

    try:
        code, out, err = run_cli(["generate", "e1"] + project.config_args())
    except KeyboardInterrupt:
        pytest.fail(
            "a KeyboardInterrupt escaped agf.cli.main uncaught instead of being "
            "reported as one JSON document with exit code 11 (R4/R28)"
        )

    doc = parse_single_json_document(out)
    assert code == 11
    assert doc["ok"] is False

    # R68: an interrupt removes the staging directory, then the marker.
    assert list(project.drafts.rglob(".agf-tmp-*")) == []
    assert list(project.drafts.rglob(".agf-old-*")) == []
    assert not (project.drafts / "e1.png").exists()
    assert not project.record_path.exists()


# ---------------------------------------------------------------------------
# 4. The API token is sent to model-controlled result URLs.
# ---------------------------------------------------------------------------

def test_defect4_credential_is_not_sent_when_fetching_a_result_file(real_provider_fake_http):
    """
    `_get_bytes` (agf/provider.py) reuses `run`'s Authorization header to
    fetch every URL in the prediction's `output`, and that URL is entirely
    provider/model-controlled — R31 forbids the credential from appearing
    anywhere the model could see or redirect it to. Replicate's result
    files are pre-signed and need no auth at all.
    """
    http = real_provider_fake_http
    output_url = "https://delivery.replicate.com/xyz/out.png"
    http.queue_post(
        FakeResponse(
            json_data={
                "id": "pred1",
                "status": "succeeded",
                "version": "deadbeef",
                "output": output_url,
                "urls": {"get": "https://api.replicate.com/v1/predictions/pred1"},
            }
        )
    )
    http.set_get(output_url, FakeResponse(content=b"totally real image bytes"))

    secret = "sekrit-token-must-not-leak-to-model-controlled-urls"
    result = REAL_PROVIDER_RUN("owner/model", {"prompt": "a cat"}, secret)

    assert result["outputs"] == [b"totally real image bytes"]
    output_fetch_calls = [c for c in http.get_calls if c["url"] == output_url]
    assert len(output_fetch_calls) == 1
    headers_sent = output_fetch_calls[0]["headers"]
    assert "Authorization" not in headers_sent, (
        f"the credential was sent to a model-controlled result URL: {headers_sent}"
    )
    assert secret not in json.dumps(headers_sent)


# ---------------------------------------------------------------------------
# 5. A malformed extract_frames template decodes the whole video first.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_template",
    ["frames/w_{n}_{x}.png", "frames/w_{n}_{0}.png", "frames/w_{n}_{.png"],
    ids=["extra-named-field", "extra-positional-field", "unbalanced-brace"],
)
def test_defect5_malformed_template_exits_3_and_never_calls_extraction(
    project, run_cli, bad_template
):
    """
    `_validate_template_syntax` (agf/manifest.py) only counts `{n}`
    occurrences; it never confirms the rest of the string is a safe format
    string for `str.format`. Each of these currently passes validation,
    decodes the whole video, and only then fails formatting a basename. The
    default autouse extraction guard (conftest.py) proves extraction was
    never reached — if it had run, this would see exit 11 from the guard's
    own AssertionError, never exit 3.
    """
    entry = extract_frames_entry(name="f1", output=bad_template)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc


# ---------------------------------------------------------------------------
# 6. A corrupt record file lets the asset and the record diverge.
# ---------------------------------------------------------------------------

def test_defect6_corrupt_record_exits_13_and_never_lets_asset_and_record_diverge(
    project, run_cli, fake_provider, monkeypatch
):
    """
    `load_record` (agf/record.py) has no try/except around `json.loads`.
    Today, with unparseable JSON already at the record path, `execute_entry`
    commits the new asset first (it never touches the record); only then
    does `write_record` read the existing file, raise uncaught, and leave
    a brand-new committed asset with no matching record entry, forever,
    beside a record file that is exactly as corrupt as it started.

    R76 is now settled: any record the framework cannot read as a valid
    record exits 13, detected before anything is committed or spent, with
    an error stating the record may be deleted. The exit code is the
    mechanism; the guarantee it exists to protect — the asset and its
    record never diverging, which R53 promises — is still the thing this
    test is really about, so both are asserted.
    """
    project.record_path.write_text("{not valid json at all:::")
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", output="e1.png", format="png")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})

    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 13, doc

    asset_committed = (project.drafts / "e1.png").exists()
    record_has_the_new_entry = False
    try:
        record = json.loads(project.record_path.read_text())
        record_has_the_new_entry = "e1" in record.get("entries", {})
    except (json.JSONDecodeError, OSError):
        record_has_the_new_entry = False

    assert not (asset_committed and not record_has_the_new_entry), (
        "the asset was committed to drafts but the record does not hold a "
        "matching entry for it — the asset and its record have diverged"
    )


# ---------------------------------------------------------------------------
# Coverage gap: R76 pinned for one shape through one command only, which
# does not test what R76 actually promises — the requirement is structural
# ("whatever prevents the file being read as a record puts it on this
# path"), and it applies to all four commands alike.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", ["list", "record", "generate", "regenerate"])
@pytest.mark.parametrize(
    "label,content_bytes",
    [
        ("empty_file", b""),
        ("top_level_not_object_list", b"[]"),
        ("top_level_not_object_number", b"42"),
        ("entries_missing", b'{"version": 1}'),
        ("entries_not_object", b'{"version": 1, "entries": []}'),
        ("entry_not_object", b'{"version": 1, "entries": {"x": "not-a-dict"}}'),
        # Not one of R76's own illustrative shapes. R76 says the list is
        # "illustrative, not exhaustive" and the whole read (not just the
        # JSON parse) is guarded — this fails a step earlier than "does not
        # parse as JSON": it is not even valid text.
        ("not_valid_utf8", b"\x80\x81\x82 not even decodable as text"),
    ],
)
def test_r76_every_unreadable_shape_exits_13_on_every_command(
    project, run_cli, command, label, content_bytes
):
    project.record_path.write_bytes(content_bytes)
    if command == "list":
        args = ["list"]
    else:
        args = [command, "whatever-entry-name"]

    code, out, _ = run_cli(args + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 13, (command, label, doc)


# ---------------------------------------------------------------------------
# 7. A non-JSON provider response body escapes the boundary.
# ---------------------------------------------------------------------------

def test_defect7_non_json_provider_body_is_exit_6_not_internal(
    project, run_cli, real_provider_fake_http, monkeypatch
):
    """
    `_post_json` (agf/provider.py) calls `response.json()` outside its own
    try/except, so a 200 response with a non-JSON body (an HTML error page,
    say) is not treated as the provider/transport failure it is — R33/R75
    say a rejected request or transport failure is `ProviderError`, exit 6,
    with the provider's own text in `message`; today it is R28's internal
    failure, exit 11, with a raw traceback on stderr instead.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen")
    write_manifest(project, [entry])

    bad_json = json.JSONDecodeError("Expecting value", "<html>internal server error</html>", 0)
    real_provider_fake_http.queue_post(FakeResponse(json_exc=bad_json))

    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 6, doc
    assert doc["error"]["message"]


# ---------------------------------------------------------------------------
# 8. The poll loop never terminates.
# ---------------------------------------------------------------------------

def test_defect8_poll_loop_gives_up_instead_of_spinning_forever(real_provider_fake_http):
    """
    `run`'s poll loop (agf/provider.py) has no attempt cap; a prediction
    resource that never carries a recognisable `status` (malformed, not
    slow) loops forever, holding the run lock the whole time. R32 forbids a
    *timeout on a genuine prediction* — that is not this: a response that
    never becomes parseable is not a prediction taking a long time, it is a
    provider that is not answering the question.

    The exact number of attempts before giving up is not something this
    PRD decides — see the report. This only asserts that it gives up well
    inside a deliberately generous, arbitrary sanity backstop; any
    reasonable real cap clears it with room to spare, and `time.sleep` is
    replaced with a no-op so this runs in milliseconds either way.
    """
    http = real_provider_fake_http
    http.queue_post(
        FakeResponse(
            json_data={
                "id": "pred1",
                "status": "starting",
                "urls": {"get": "https://api.replicate.com/v1/predictions/pred1"},
            }
        )
    )

    SANITY_BACKSTOP = 2000

    def _malformed_response_forever(call_number):
        if call_number > SANITY_BACKSTOP:
            raise AssertionError(
                f"provider.run polled more than {SANITY_BACKSTOP} times without giving "
                "up on a response that never carries a recognisable status"
            )
        return FakeResponse(json_data={"id": "pred1"})  # no "status" key, ever

    http.set_get("https://api.replicate.com/v1/predictions/pred1", _malformed_response_forever)

    with pytest.raises(provider_module.ProviderError):
        REAL_PROVIDER_RUN("owner/model", {}, "token")


# ---------------------------------------------------------------------------
# 9. A non-image file named *.png in `frames:` crashes instead of failing
#    the frame_size check.
# ---------------------------------------------------------------------------

def test_defect9_non_image_frame_is_exit_7_frame_size_fail_not_internal(project, run_cli):
    """
    `check_frame_sizes` (agf/checks.py) calls `Image.open(path)` with no
    try/except; a file matching `frames:` by name and extension but not
    actually decodable as an image raises `PIL.UnidentifiedImageError`
    uncaught. R61 puts exactly this at exit 7 with `frame_size: "fail"` —
    a frame the framework cannot even read is not a size mismatch by
    coincidence, but it is still a `frame_size` failure, not an internal one.
    """
    frames_dir = project.samples / "frames"
    make_png(frames_dir / "f0.png")
    (frames_dir / "f1.png").write_bytes(b"not an image, just named like one")
    make_png(frames_dir / "f2.png")
    make_png(frames_dir / "f3.png")
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


# ---------------------------------------------------------------------------
# 10. Failed checks must name the declared value and the actual one.
# ---------------------------------------------------------------------------

def test_defect10_format_failure_names_declared_and_actual_format(
    project, run_cli, fake_provider, monkeypatch
):
    """R54: message must state the declared format and what the bytes
    actually are — today every check failure produces the identical
    generic string regardless of which check failed or why."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", output="e1.png", format="png")
    write_manifest(project, [entry])
    # detect_format sniffs \xff\xd8 as jpeg regardless of what follows.
    not_a_png = b"\xff\xd8\xff" + b"this is not a png, it is jpeg-shaped"
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [not_a_png]})

    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7, doc
    message = doc["error"]["message"].lower()
    assert "png" in message, f"declared format 'png' not named in: {message!r}"
    assert "jpeg" in message, f"actual detected format 'jpeg' not named in: {message!r}"


def test_defect10_layout_failure_names_declared_and_actual_dimensions(
    project, run_cli, fake_provider, monkeypatch
):
    """R57: message must state both the declared and actual sheet
    dimensions."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(
        name="sh1", output="sh1.png", frame_count=4, frame_size=(10, 10),
        layout={"columns": 2, "rows": 2},
    )
    write_manifest(project, [entry])
    wrong_sheet = png_bytes(size=(19, 20))  # declared 20x20, actually 19x20
    fake_provider(run_result={"version": "acme/sheetmaker:v1", "seed": None, "outputs": [wrong_sheet]})

    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7, doc
    message = doc["error"]["message"]
    assert "20" in message, f"declared dimension '20' not named in: {message!r}"
    assert "19" in message, f"actual dimension '19' not named in: {message!r}"


def test_defect10_frame_size_failure_names_offending_frame_and_sizes(project, run_cli):
    """R61: message must name the offending frame, its actual size, and the
    declared frame_size."""
    frames_dir = project.samples / "frames"
    make_png(frames_dir / "f0.png", size=(10, 10))
    make_png(frames_dir / "f1.png", size=(5, 5))  # the offender
    make_png(frames_dir / "f2.png", size=(10, 10))
    make_png(frames_dir / "f3.png", size=(10, 10))
    entry = sheet_assemble_entry(
        name="sheet1", frames=[f"samples:frames/f{i}.png" for i in range(4)]
    )
    write_manifest(project, [entry])

    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7, doc
    message = doc["error"]["message"]
    assert "f1.png" in message, f"offending frame not named in: {message!r}"
    assert "5" in message, f"actual frame size '5' not named in: {message!r}"
    assert "10" in message, f"declared frame_size '10' not named in: {message!r}"


# ---------------------------------------------------------------------------
# Also flagged: two single-file entries declaring the identical `output`.
# ---------------------------------------------------------------------------

def test_gap_two_single_file_entries_sharing_one_output_is_rejected(project, run_cli):
    """
    `_validate_cross_entry_claims` (agf/manifest.py) checks claimed-
    directory-vs-claimed-directory overlap and a single file sitting inside
    a claimed directory, but never compares two ordinary (non-
    extract_frames) entries' `output` against each other — two entries
    declaring the exact same path both validate today. Whichever commits
    second silently overwrites the first's file and record entry with no
    collision ever signalled, which is the same cross-entry mistake R63's
    containment rule exists to catch, just in its most basic form.
    """
    entries = [
        image_model_entry(name="a", model="acme/x", output="shared.png"),
        image_model_entry(name="b", model="acme/y", output="shared.png"),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3, doc
