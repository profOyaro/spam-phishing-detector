"""Email parsing utilities for raw text and RFC822 .eml files."""
from __future__ import annotations
from email import policy
from email.parser import BytesParser, Parser


def parse_eml_bytes(content: bytes) -> dict:
    """Parse uploaded .eml content into headers, text body, and attachments."""
    msg = BytesParser(policy=policy.default).parsebytes(content)
    text_parts: list[str] = []
    attachments: list[tuple[str, int]] = []

    if msg.is_multipart():
        for part in msg.walk():
            disposition = part.get_content_disposition()
            if disposition == "attachment":
                payload = part.get_payload(decode=True) or b""
                attachments.append((part.get_filename() or "attachment", len(payload)))
            elif part.get_content_type() == "text/plain":
                try:
                    text_parts.append(part.get_content())
                except Exception:
                    pass
    else:
        try:
            text_parts.append(msg.get_content())
        except Exception:
            text_parts.append(content.decode("utf-8", errors="ignore"))

    return {
        "from": msg.get("from", ""),
        "subject": msg.get("subject", ""),
        "body": "\n".join(text_parts),
        "raw": content.decode("utf-8", errors="ignore"),
        "attachments": attachments,
    }


def parse_raw_text(raw_text: str) -> dict:
    """Parse plain pasted text, preserving raw content for header analysis."""
    msg = Parser(policy=policy.default).parsestr(raw_text or "")
    body = msg.get_body(preferencelist=("plain",))
    return {
        "from": msg.get("from", ""),
        "subject": msg.get("subject", ""),
        "body": body.get_content() if body else raw_text,
        "raw": raw_text,
        "attachments": [],
    }
