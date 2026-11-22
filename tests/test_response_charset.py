"""A body whose Content-Type names no charset is decoded by what the page says, not as Latin-1."""

from citeget.netguard import GuardedResponse


def _response(body: bytes, content_type: str | None) -> GuardedResponse:
    r = GuardedResponse()
    r._content = body
    r._content_consumed = True
    r.status_code = 200
    if content_type:
        r.headers["Content-Type"] = content_type
        if "charset" not in content_type:
            r.encoding = "ISO-8859-1"  # what requests assumes for a bare text/*
    return r


def test_meta_charset_beats_the_latin1_default():
    body = '<html><head><meta charset="utf-8"></head><body>passé</body></html>'.encode()
    assert "passé" in _response(body, "text/html").text


def test_http_equiv_meta_is_read_too():
    body = (
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        "<p>café</p>"
    ).encode()
    assert "café" in _response(body, "text/html").text


def test_bytes_are_guessed_when_the_page_declares_nothing():
    body = ("<p>" + "passé, où, déjà, très, façon. " * 20 + "</p>").encode()
    assert "passé" in _response(body, "text/html").text


def test_a_declared_charset_is_respected():
    body = "<p>passé</p>".encode("latin-1")
    assert "passé" in _response(body, "text/html; charset=iso-8859-1").text
