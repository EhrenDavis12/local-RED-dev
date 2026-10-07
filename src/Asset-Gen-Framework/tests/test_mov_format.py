"""
`mov` is a declared video format: a QuickTime container is what carries an
alpha channel (ProRes 4444) back from a video matting model, and the byte
check has to tell it from an MP4, which shares the ftyp box.
"""
from __future__ import annotations

from agf.checks import check_format, detect_format


def _ftyp(brand: bytes) -> bytes:
    return b"\x00\x00\x00\x14ftyp" + brand + b"\x00\x00\x00\x00" + brand + b"\x00" * 32


def test_quicktime_brand_is_mov_and_isom_is_mp4():
    assert detect_format(_ftyp(b"qt  ")) == "mov"
    assert detect_format(_ftyp(b"isom")) == "mp4"


def test_declared_mov_fails_on_mp4_bytes_and_vice_versa():
    assert check_format(_ftyp(b"qt  "), "mov")[0] == "pass"
    assert check_format(_ftyp(b"isom"), "mov")[0] == "fail"
    assert check_format(_ftyp(b"qt  "), "mp4")[0] == "fail"
