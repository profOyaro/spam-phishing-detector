from app.attachment_scanner import scan
def test_exe(): assert scan("invoice.pdf.exe", b"MZ...")["score"] >= 60
